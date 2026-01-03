from typing import List, Dict, Any, Tuple
from core.llm_client import openrouter_client
import numpy as np
from core.database import Feedback, Theme
from sqlalchemy.orm import Session

# Try to import sklearn, fallback to simple clustering if not available
try:
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class FeedbackClustering:
    """Cluster feedback into themes using embeddings"""
    
    def __init__(self):
        self.llm_client = openrouter_client
    
    async def cluster_feedback(
        self,
        feedback_items: List[Dict[str, Any]],
        db: Session
    ) -> List[Dict[str, Any]]:
        """Cluster feedback items into themes - QUARTER-AWARE: Only clusters feedback within the same quarter"""
        from core.database import Feedback, Theme  # Import at function start
        from datetime import datetime
        
        if not feedback_items:
            return []
        
        # Group feedback by quarter first (Q1, Q2, Q3, Q4 + year)
        # This ensures themes only contain feedback from the same quarter
        quarter_groups = {}
        
        for item in feedback_items:
            # Get created_at date from item
            created_at = item.get("created_at")
            if created_at is None:
                # Try to get from database if item has an ID
                if "id" in item:
                    from core.database import Feedback
                    feedback_obj = db.query(Feedback).filter(Feedback.id == item["id"]).first()
                    if feedback_obj and feedback_obj.created_at:
                        created_at = feedback_obj.created_at
            
            if isinstance(created_at, str):
                try:
                    # Parse date string
                    if 'T' in created_at:
                        created_at = created_at.split('+')[0].split('Z')[0].split('.')[0]
                    created_at = datetime.fromisoformat(created_at)
                except:
                    created_at = None
            elif not isinstance(created_at, datetime):
                created_at = None
            
            # Determine quarter
            if created_at:
                year = created_at.year
                month = created_at.month
                if month <= 3:
                    quarter = 'Q1'
                elif month <= 6:
                    quarter = 'Q2'
                elif month <= 9:
                    quarter = 'Q3'
                else:
                    quarter = 'Q4'
                quarter_key = f"{quarter}_{year}"
            else:
                # If no date, use current quarter as fallback
                now = datetime.now()
                year = now.year
                month = now.month
                if month <= 3:
                    quarter = 'Q1'
                elif month <= 6:
                    quarter = 'Q2'
                elif month <= 9:
                    quarter = 'Q3'
                else:
                    quarter = 'Q4'
                quarter_key = f"{quarter}_{year}"
            
            if quarter_key not in quarter_groups:
                quarter_groups[quarter_key] = []
            quarter_groups[quarter_key].append(item)
        
        print(f"  📅 Grouped feedback into {len(quarter_groups)} quarter groups: {list(quarter_groups.keys())}")
        
        # Cluster each quarter group separately
        all_themes = []
        for quarter_key, quarter_items in quarter_groups.items():
            print(f"  📊 Clustering {len(quarter_items)} items for {quarter_key}...")
            quarter_themes = await self._cluster_quarter_feedback(quarter_items, quarter_key, db)
            all_themes.extend(quarter_themes)
        
        return all_themes
    
    async def _cluster_quarter_feedback(
        self,
        feedback_items: List[Dict[str, Any]],
        quarter_key: str,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Cluster feedback items within a single quarter"""
        if not feedback_items:
            return []
        
        try:
            # Get embeddings for all feedback - use full content for better similarity matching
            texts = []
            valid_items = []
            for item in feedback_items:
                content = item.get("content", "")
                if content and content.strip():
                    # Use full content (up to 500 chars) for better similarity matching
                    texts.append(content[:500])
                    valid_items.append(item)
            
            if not texts:
                print("  ⚠️ No valid content found for clustering")
                return []
            
            print(f"  📊 Getting embeddings for {len(texts)} feedback items...")
            print(f"     Sample contents: {[t[:50] + '...' for t in texts[:3]]}")
            embeddings = await self.llm_client.embeddings(texts)
            print(f"  ✅ Got {len(embeddings)} embeddings")
            
            # Update valid_feedback_items to match texts
            feedback_items = valid_items
        except Exception as embed_error:
            print(f"  ❌ Error getting embeddings: {str(embed_error)}")
            import traceback
            traceback.print_exc()
            return []  # Return empty themes if embeddings fail
        
        try:
            # Use cosine similarity-based clustering (better for embeddings than euclidean distance)
            # This groups similar feedback requests together based on semantic similarity
            print(f"  📊 Using cosine similarity clustering to group similar requests...")
            cluster_labels = self._cosine_similarity_clustering(embeddings)
            unique_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
            noise_count = list(cluster_labels).count(-1)
            print(f"  📊 Cosine similarity clustering: {unique_clusters} clusters, {noise_count} noise points")
            
            # Map valid texts back to original feedback items
            valid_feedback_items = [item for item in feedback_items if item.get("content", "").strip()]
            
            # Group feedback by cluster
            clusters = {}
            noise_items = []  # Store noise points separately to try merging them
            
            for idx, label in enumerate(cluster_labels):
                if idx >= len(valid_feedback_items):
                    continue
                if label == -1:  # Noise points - try to merge with similar clusters first
                    noise_items.append((idx, valid_feedback_items[idx]))
                else:
                    if label not in clusters:
                        clusters[label] = []
                    clusters[label].append(valid_feedback_items[idx])
            
            # Try to merge noise points with existing clusters if they're similar enough
            unmerged_noise_items = []  # Keep (idx, item) tuples for final merge attempt
            if noise_items and clusters:
                embeddings_array = np.array(embeddings)
                for noise_idx, noise_item in noise_items:
                    noise_embedding = embeddings_array[noise_idx]
                    best_cluster = None
                    best_similarity = 0.0
                    similarity_threshold = 0.35  # Very low threshold (0.35) for aggressive grouping of similar requests
                    
                    # Find the most similar cluster
                    for cluster_id, cluster_items in clusters.items():
                        # Get average embedding of cluster
                        cluster_indices = [valid_feedback_items.index(item) for item in cluster_items if item in valid_feedback_items]
                        if cluster_indices:
                            cluster_embeddings = embeddings_array[cluster_indices]
                            cluster_avg = np.mean(cluster_embeddings, axis=0)
                            
                            # Calculate cosine similarity
                            dot_product = np.dot(noise_embedding, cluster_avg)
                            norm_noise = np.linalg.norm(noise_embedding)
                            norm_cluster = np.linalg.norm(cluster_avg)
                            if norm_noise > 0 and norm_cluster > 0:
                                similarity = dot_product / (norm_noise * norm_cluster)
                                if similarity > best_similarity and similarity >= similarity_threshold:
                                    best_similarity = similarity
                                    best_cluster = cluster_id
                    
                    # Add to best cluster if similar enough
                    if best_cluster is not None:
                        clusters[best_cluster].append(noise_item)
                        print(f"  🔗 Merged noise item into cluster {best_cluster} (similarity: {best_similarity:.3f})")
                    else:
                        # Keep as unmerged for final merge attempt
                        unmerged_noise_items.append((noise_idx, noise_item))
            else:
                # No clusters exist, all items are noise - keep with indices for final merge
                unmerged_noise_items = noise_items
            
            # Final merge attempt: try to merge remaining single items into existing clusters with even tighter threshold
            final_unmerged = []
            if unmerged_noise_items and clusters:
                embeddings_array = np.array(embeddings)
                for noise_idx, noise_item in unmerged_noise_items:
                    noise_embedding = embeddings_array[noise_idx]
                    best_cluster = None
                    best_similarity = 0.0
                    # Very low threshold for final merge attempt (0.30 = extremely aggressive grouping)
                    final_threshold = 0.30
                    
                    for cluster_id, cluster_items in clusters.items():
                        cluster_indices = [valid_feedback_items.index(item) for item in cluster_items if item in valid_feedback_items]
                        if cluster_indices:
                            cluster_embeddings = embeddings_array[cluster_indices]
                            cluster_avg = np.mean(cluster_embeddings, axis=0)
                            
                            dot_product = np.dot(noise_embedding, cluster_avg)
                            norm_noise = np.linalg.norm(noise_embedding)
                            norm_cluster = np.linalg.norm(cluster_avg)
                            if norm_noise > 0 and norm_cluster > 0:
                                similarity = dot_product / (norm_noise * norm_cluster)
                                if similarity > best_similarity and similarity >= final_threshold:
                                    best_similarity = similarity
                                    best_cluster = cluster_id
                    
                    if best_cluster is not None:
                        clusters[best_cluster].append(noise_item)
                        print(f"  🔗 Final merge: Added single item to cluster {best_cluster} (similarity: {best_similarity:.3f})")
                    else:
                        final_unmerged.append(noise_item)
            else:
                # No clusters or no unmerged items
                final_unmerged = [item for _, item in unmerged_noise_items] if unmerged_noise_items else []
            
            # Log clustering results
            print(f"  📊 Clustering results: {len(clusters)} clusters found")
            for cluster_id, items in clusters.items():
                print(f"    Cluster {cluster_id}: {len(items)} items")
            
            themes = []
            single_items_from_clusters = []  # Track single items from clusters separately
            
            # FIRST: Only create themes for clusters with 2+ items (similar requests grouped together)
            # Single items will be merged into existing themes later
            for cluster_id, items in clusters.items():
                try:
                    # Only create themes for clusters with 2+ similar items grouped together
                    if len(items) >= 2:
                        theme = await self.create_theme_from_cluster(cluster_id, items, db)
                        if theme:  # Only add if theme creation succeeded
                            themes.append(theme)
                            print(f"  ✅ Created theme '{theme.get('name', 'Unknown')}' with {len(items)} similar requests grouped together")
                    else:
                        # Single items from clusters - add to list for merging with existing themes
                        single_items_from_clusters.extend(items)
                        print(f"  🔄 Deferring {len(items)} single item(s) from cluster {cluster_id} for merging with existing themes")
                except Exception as theme_error:
                    print(f"  ⚠️ Error creating theme for cluster {cluster_id}: {str(theme_error)}")
                    import traceback
                    traceback.print_exc()
                    continue  # Continue with other clusters
            
            # Combine all single items (from noise and from single-item clusters) for merging
            all_single_items = final_unmerged + single_items_from_clusters
            
            # Try one more aggressive merge pass for remaining single items
            if all_single_items and themes:
                print(f"  🔄 Attempting final aggressive merge for {len(all_single_items)} ungrouped items...")
                # Get all existing theme embeddings for comparison
                existing_themes = db.query(Theme).filter(Theme.id.in_([t.get('id') for t in themes if t.get('id')])).all()
                
                if existing_themes:
                    # Get sample feedback from each theme to create embeddings
                    theme_samples = []
                    for theme in existing_themes:
                        theme_feedback = db.query(Feedback).filter(Feedback.theme_id == theme.id).limit(3).all()
                        if theme_feedback:
                            sample_text = " ".join([f.content[:200] for f in theme_feedback[:3]])
                            theme_samples.append((theme.id, sample_text))
                    
                    if theme_samples:
                        sample_texts = [text for _, text in theme_samples]
                        try:
                            theme_embeddings = await self.llm_client.embeddings(sample_texts)
                            theme_emb_dict = {theme_samples[i][0]: theme_embeddings[i] for i in range(len(theme_samples))}
                            
                            # Get embeddings for ALL unmerged items (both noise and single-item clusters)
                            unmerged_texts = [item.get("content", "")[:500] for item in all_single_items]
                            unmerged_embeddings = await self.llm_client.embeddings(unmerged_texts)
                            
                            # Try to merge each unmerged item with existing themes
                            merged_count = 0
                            for item_idx, (noise_item, item_embedding) in enumerate(zip(all_single_items, unmerged_embeddings)):
                                best_theme_id = None
                                best_similarity = 0.0
                                merge_threshold = 0.30  # Extremely aggressive threshold to merge similar items
                                
                                for theme_id, theme_embedding in theme_emb_dict.items():
                                    # Calculate cosine similarity
                                    dot_product = np.dot(item_embedding, theme_embedding)
                                    norm_item = np.linalg.norm(item_embedding)
                                    norm_theme = np.linalg.norm(theme_embedding)
                                    if norm_item > 0 and norm_theme > 0:
                                        similarity = dot_product / (norm_item * norm_theme)
                                        if similarity > best_similarity and similarity >= merge_threshold:
                                            best_similarity = similarity
                                            best_theme_id = theme_id
                                
                                if best_theme_id:
                                    # Link this feedback item to the existing theme
                                    if "id" in noise_item:
                                        feedback = db.query(Feedback).filter(Feedback.id == noise_item["id"]).first()
                                        if feedback:
                                            feedback.theme_id = best_theme_id
                                            merged_count += 1
                                            print(f"  🔗 Merged item into existing theme {best_theme_id} (similarity: {best_similarity:.3f})")
                            
                            if merged_count > 0:
                                db.commit()
                                print(f"  ✅ Merged {merged_count} items into existing themes")
                        except Exception as merge_error:
                            print(f"  ⚠️ Error in final merge attempt: {str(merge_error)}")
            
            # Create individual themes for remaining items that couldn't be grouped
            remaining_unmerged = []
            for item in all_single_items:
                if "id" in item:
                    feedback = db.query(Feedback).filter(Feedback.id == item["id"]).first()
                    if feedback and not feedback.theme_id:
                        remaining_unmerged.append(item)
                else:
                    remaining_unmerged.append(item)
            for noise_item in remaining_unmerged:
                try:
                    # Create theme for single item when no similar items are found
                    theme = await self.create_theme_from_cluster(f"single_{len(themes)}", [noise_item], db)
                    if theme:
                        themes.append(theme)
                        print(f"  📝 Created individual theme '{theme.get('name', 'Unknown')}' (no similar requests found)")
                except Exception as theme_error:
                    print(f"  ⚠️ Error creating individual theme: {str(theme_error)}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            grouped_items_count = sum(len(items) for items in clusters.values() if len(items) >= 2)
            print(f"  ✅ Created {len(themes)} themes with {grouped_items_count} similar requests grouped together, {len(remaining_unmerged)} individual items")
            return themes
        except Exception as cluster_error:
            print(f"  ❌ Error in clustering: {str(cluster_error)}")
            import traceback
            traceback.print_exc()
            return []  # Return empty themes if clustering fails
    
    def _cosine_similarity_clustering(self, embeddings: List[List[float]]) -> List[int]:
        """Cosine similarity-based clustering - groups similar items together
        This is better for embeddings than euclidean distance-based clustering"""
        if len(embeddings) <= 1:
            return [-1] if embeddings else []
        
        embeddings_array = np.array(embeddings)
        n = len(embeddings)
        cluster_labels = [-1] * n  # Start all as noise
        cluster_id = 0
        # Use a higher threshold (0.80) to group only very similar feedback requests
        # This will group items that are about the same specific issue/topic
        # but won't group everything together
        threshold = 0.80
        
        # Calculate all similarities first for debugging
        similarities = []
        for i in range(min(5, n)):  # Sample first 5 items
            for j in range(i + 1, min(i + 6, n)):  # Compare with next 5 items
                dot_product = np.dot(embeddings_array[i], embeddings_array[j])
                norm_i = np.linalg.norm(embeddings_array[i])
                norm_j = np.linalg.norm(embeddings_array[j])
                if norm_i > 0 and norm_j > 0:
                    similarity = dot_product / (norm_i * norm_j)
                    similarities.append(similarity)
        
        if similarities:
            avg_sim = np.mean(similarities)
            max_sim = np.max(similarities)
            min_sim = np.min(similarities)
            print(f"    Similarity stats (sample): min={min_sim:.3f}, avg={avg_sim:.3f}, max={max_sim:.3f}, threshold={threshold}")
        
        # First pass: Find groups of similar items
        for i in range(n):
            if cluster_labels[i] != -1:
                continue
            
            # Try to find similar items to group with
            similar_items = [i]
            for j in range(i + 1, n):
                if cluster_labels[j] == -1:
                    # Calculate cosine similarity
                    dot_product = np.dot(embeddings_array[i], embeddings_array[j])
                    norm_i = np.linalg.norm(embeddings_array[i])
                    norm_j = np.linalg.norm(embeddings_array[j])
                    if norm_i > 0 and norm_j > 0:
                        similarity = dot_product / (norm_i * norm_j)
                        if similarity >= threshold:
                            similar_items.append(j)
            
            # Create cluster if we have 2+ similar items (group them together)
            if len(similar_items) >= 2:
                for idx in similar_items:
                    cluster_labels[idx] = cluster_id
                cluster_id += 1
                print(f"    Created cluster {cluster_id-1} with {len(similar_items)} similar items")
        
        # Second pass: Try to merge single items into existing clusters with slightly lower threshold
        single_items = [i for i in range(n) if cluster_labels[i] == -1]
        if single_items and cluster_id > 0:
            print(f"    Attempting to merge {len(single_items)} single items into existing clusters...")
            merge_threshold = 0.75  # Slightly lower threshold (0.75) for merging singles into existing clusters
            
            for single_idx in single_items:
                best_cluster = None
                best_similarity = 0.0
                
                # Find the best cluster to merge into
                for cluster_id_check in range(cluster_id):
                    cluster_members = [i for i in range(n) if cluster_labels[i] == cluster_id_check]
                    if cluster_members:
                        # Calculate average embedding of cluster
                        cluster_embeddings = embeddings_array[cluster_members]
                        cluster_avg = np.mean(cluster_embeddings, axis=0)
                        
                        # Calculate cosine similarity with cluster average
                        dot_product = np.dot(embeddings_array[single_idx], cluster_avg)
                        norm_single = np.linalg.norm(embeddings_array[single_idx])
                        norm_cluster = np.linalg.norm(cluster_avg)
                        if norm_single > 0 and norm_cluster > 0:
                            similarity = dot_product / (norm_single * norm_cluster)
                            if similarity > best_similarity and similarity >= merge_threshold:
                                best_similarity = similarity
                                best_cluster = cluster_id_check
                
                # Merge into best cluster if found
                if best_cluster is not None:
                    cluster_labels[single_idx] = best_cluster
                    # Update cluster size in log
                    cluster_members = [i for i in range(n) if cluster_labels[i] == best_cluster]
                    print(f"    Merged single item into cluster {best_cluster} (similarity: {best_similarity:.3f}, cluster now has {len(cluster_members)} items)")
        
        return cluster_labels
    
    def _simple_clustering(self, embeddings: List[List[float]]) -> List[int]:
        """Simple similarity-based clustering fallback when sklearn is not available
        Groups similar items together when found, otherwise leaves as noise for individual themes"""
        # Use the cosine similarity clustering method
        return self._cosine_similarity_clustering(embeddings)
    
    async def create_theme_from_cluster(
        self,
        cluster_id: Any,
        items: List[Dict[str, Any]],
        db: Session
    ) -> Dict[str, Any]:
        """Create a theme from a cluster of feedback items"""
        # Generate theme name and description
        contents = [item.get("content", "")[:200] for item in items[:5]]
        theme_prompt = f"""Based on these feedback items, create a theme:

{chr(10).join(contents)}

Return JSON with:
- name: concise theme name (3-5 words)
- description: 2-3 sentence description
"""
        
        response = await self.llm_client.chat_completion([
            {"role": "system", "content": "You create themes from feedback clusters. Return valid JSON."},
            {"role": "user", "content": theme_prompt}
        ], temperature=0.5)
        
        try:
            import json
            theme_data = json.loads(response)
            # Handle case where LLM returns a list instead of dict
            if isinstance(theme_data, list):
                if len(theme_data) > 0 and isinstance(theme_data[0], dict):
                    theme_data = theme_data[0]  # Use first item if it's a list of dicts
                else:
                    raise ValueError("Invalid theme_data format")
            # Ensure it's a dict
            if not isinstance(theme_data, dict):
                raise ValueError("theme_data is not a dict")
        except Exception as e:
            print(f"⚠️ Error parsing theme data: {e}, using fallback")
            theme_data = {
                "name": f"Theme {cluster_id}",
                "description": f"Cluster of {len(items)} feedback items"
            }
        
        # Calculate theme metrics
        request_frequency = len(items)
        sentiment_scores = [item.get("sentiment_score", 0) for item in items if item.get("sentiment_score")]
        pain_levels = [item.get("pain_level", 0) for item in items if item.get("pain_level")]
        
        customer_value = np.mean(pain_levels) if pain_levels else 5.0
        trend_velocity = await self.calculate_trend_velocity(items)
        
        # Create theme object (but don't commit yet - we need to link feedback first)
        theme = Theme(
            name=theme_data.get("name", f"Theme {cluster_id}"),
            description=theme_data.get("description", ""),
            request_frequency=request_frequency,
            customer_value=customer_value,
            trend_velocity=trend_velocity,
            strategic_segment_weight=0.5,  # Default, can be calculated
            competitive_pressure=0.5,  # Default
            recency_score=await self.calculate_recency_score(items),
            overall_impact_score=0.0  # Will be calculated IMMEDIATELY before commit
        )
        
        db.add(theme)
        db.flush()  # Get theme ID without committing
        
        # Link feedback items to theme FIRST (needed for impact score calculation)
        for item in items:
            if "id" in item:
                feedback = db.query(Feedback).filter(Feedback.id == item["id"]).first()
                if feedback:
                    feedback.theme_id = theme.id
        
        # NOW calculate impact score with ARR, lost deals, etc. BEFORE committing
        # This ensures theme is created with proper impact score from the start
        from core.impact_scoring import ImpactScorer
        impact_scorer = ImpactScorer()
        
        # Use LLM to detect lost deals, ARR, and competitors from theme content
        lost_deal_info = await impact_scorer.detect_lost_deals_with_llm(theme, db)
        
        # Store lost deal info in theme metadata before calculating impact score
        if not hasattr(theme, 'extra_metadata') or theme.extra_metadata is None:
            theme.extra_metadata = {}
        theme.extra_metadata["lost_deal_info"] = lost_deal_info
        
        # Now calculate impact score (which will use the lost_deal_info we just set)
        theme.overall_impact_score = impact_scorer.calculate_theme_impact_score(theme, db)
        
        # Commit once with everything: theme, feedback links, and impact score
        db.commit()
        db.refresh(theme)
        
        # Get ARR and lost deal info for return value (use aggregated data from ALL feedback items)
        theme_feedback = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
        
        # Get aggregated data from lost_deal_info (which aggregates ALL feedback items in the cluster)
        lost_deal_info = {}
        if theme.extra_metadata and isinstance(theme.extra_metadata, dict):
            lost_deal_info = theme.extra_metadata.get("lost_deal_info", {})
        
        # Use aggregated total_arr from lost_deal_info (which sums ALL feedback ARR in the cluster)
        total_arr_from_lost_deal_info = lost_deal_info.get("total_arr", 0)
        estimated_avg_arr = lost_deal_info.get("estimated_avg_arr", 0)
        
        # Also calculate from feedback as fallback (sum ALL feedback ARR in the cluster)
        total_arr_from_feedback = sum([f.arr for f in theme_feedback if f.arr and f.arr > 0]) if theme_feedback else 0
        arr_count = len([f for f in theme_feedback if f.arr and f.arr > 0])
        avg_arr_from_feedback = total_arr_from_feedback / arr_count if arr_count > 0 else 0
        
        # Prefer aggregated total_arr from lost_deal_info (which properly aggregates ALL items)
        if total_arr_from_lost_deal_info > 0:
            total_arr = total_arr_from_lost_deal_info
            avg_arr = estimated_avg_arr if estimated_avg_arr > 0 else (total_arr / len(theme_feedback) if theme_feedback else 0)
        elif total_arr_from_feedback > 0:
            # Use actual aggregated ARR from ALL feedback items in the cluster
            total_arr = total_arr_from_feedback
            avg_arr = avg_arr_from_feedback
        elif estimated_avg_arr > 0:
            # Fallback to estimated ARR
            avg_arr = estimated_avg_arr
            total_arr = avg_arr * len(theme_feedback) if theme_feedback else estimated_avg_arr
        else:
            avg_arr = 0
            total_arr = 0
        
        return {
            "theme_id": theme.id,
            "name": theme.name,
            "description": theme.description,
            "feedback_count": request_frequency,
            "customer_value": customer_value,
            "trend_velocity": trend_velocity,
            "impact_score": theme.overall_impact_score,  # Include impact score
            # ARR values
            "total_arr": total_arr,
            "avg_arr": avg_arr,
            # Lost deals info
            "lost_deal_count": lost_deal_info.get("lost_deal_count", 0),
            "lost_deal_arr": lost_deal_info.get("lost_deal_arr", 0),
            "competitor_mentions": lost_deal_info.get("competitor_mentions", []),
            "has_lost_deals": lost_deal_info.get("has_lost_deals", False)
        }
    
    async def calculate_trend_velocity(self, items: List[Dict[str, Any]]) -> float:
        """Calculate trend velocity based on timestamps"""
        if not items:
            return 0.0
        
        # Simple velocity calculation based on recent items
        # In production, would use actual timestamps
        return min(10.0, len(items) * 0.5)
    
    async def calculate_recency_score(self, items: List[Dict[str, Any]]) -> float:
        """Calculate recency score (0-10)"""
        # Simple recency - in production would use actual dates
        return 7.0  # Default moderate recency
    
    async def cluster_themes(
        self,
        themes: List[Theme],
        db: Session,
        similarity_threshold: float = 0.65  # Tighter threshold for theme clustering
    ) -> List[Dict[str, Any]]:
        """Cluster similar themes together into major clusters using LLM for semantic understanding
        
        Returns a list of theme clusters, where each cluster contains:
        - cluster_name: Name of the major cluster
        - cluster_description: Summary description
        - themes: List of themes merged into this cluster
        - combined_stats: Aggregated stats from all themes in cluster
        """
        if not themes or len(themes) <= 1:
            # If 0 or 1 theme, return as individual clusters
            return [{
                "cluster_name": theme.name,
                "cluster_description": theme.description or "",
                "themes": [theme],
                "combined_stats": self._calculate_cluster_stats([theme], db)
            } for theme in themes] if themes else []
        
        try:
            # First, use LLM to identify similar themes based on semantic understanding
            # This considers feedback content, not just theme names
            print(f"  🤖 Using LLM to identify similar themes from {len(themes)} themes...")
            llm_clusters = await self._llm_cluster_themes(themes, db)
            
            # If LLM clustering found clusters, use them; otherwise fall back to embedding-based
            if llm_clusters and len(llm_clusters) < len(themes):
                print(f"  ✅ LLM identified {len(llm_clusters)} clusters")
                # Convert LLM clusters to theme clusters
                theme_clusters = []
                clustered_theme_ids = set()
                
                for cluster_info in llm_clusters:
                    cluster_themes = cluster_info["themes"]
                    cluster_name = cluster_info.get("cluster_name", cluster_themes[0].name)
                    cluster_description = cluster_info.get("cluster_description", "")
                    combined_stats = self._calculate_cluster_stats(cluster_themes, db)
                    
                    # Track which themes are clustered
                    for theme in cluster_themes:
                        clustered_theme_ids.add(theme.id)
                    
                    theme_clusters.append({
                        "cluster_name": cluster_name,
                        "cluster_description": cluster_description,
                        "themes": cluster_themes,
                        "combined_stats": combined_stats,
                        "is_major_cluster": len(cluster_themes) >= 2
                    })
                
                # Add unclustered themes as individual clusters
                unclustered_themes = [t for t in themes if t.id not in clustered_theme_ids]
                for theme in unclustered_themes:
                    theme_clusters.append({
                        "cluster_name": theme.name,
                        "cluster_description": theme.description or "",
                        "themes": [theme],
                        "combined_stats": self._calculate_cluster_stats([theme], db),
                        "is_major_cluster": False
                    })
                
                # Sort by combined impact score (highest first)
                theme_clusters.sort(key=lambda c: c["combined_stats"].get("impact_score", 0), reverse=True)
                print(f"  ✅ Created {len(theme_clusters)} theme clusters using LLM ({len(llm_clusters)} major clusters, {len(unclustered_themes)} individual themes)")
                return theme_clusters
            
            # Fallback to embedding-based clustering
            print(f"  📊 Using embedding-based clustering for {len(themes)} themes...")
            
            # Get embeddings for theme names, descriptions, AND sample feedback content
            theme_texts = []
            for theme in themes:
                # Get sample feedback for this theme to include in embedding
                theme_feedback = db.query(Feedback).filter(Feedback.theme_id == theme.id).limit(3).all()
                feedback_samples = [f.content[:150] for f in theme_feedback if f.content][:3]
                feedback_text = " ".join(feedback_samples)
                
                # Combine name, description, and feedback samples for better clustering
                theme_text = f"{theme.name}. {theme.description or ''}. Sample feedback: {feedback_text}"
                theme_texts.append(theme_text)
            
            print(f"  📊 Getting embeddings for {len(theme_texts)} themes (with feedback samples)...")
            embeddings = await self.llm_client.embeddings(theme_texts)
            print(f"  ✅ Got {len(embeddings)} theme embeddings")
            
            # Cluster themes using similarity
            embeddings_array = np.array(embeddings)
            n = len(themes)
            cluster_labels = [-1] * n  # Start all as unclustered
            cluster_id = 0
            
            # Use tighter threshold for theme clustering (0.65 = more aggressive grouping)
            for i in range(n):
                if cluster_labels[i] != -1:
                    continue
                
                # Find similar themes to group with
                similar_indices = [i]
                for j in range(i + 1, n):
                    if cluster_labels[j] == -1:
                        # Calculate cosine similarity
                        dot_product = np.dot(embeddings_array[i], embeddings_array[j])
                        norm_i = np.linalg.norm(embeddings_array[i])
                        norm_j = np.linalg.norm(embeddings_array[j])
                        if norm_i > 0 and norm_j > 0:
                            similarity = dot_product / (norm_i * norm_j)
                            if similarity >= similarity_threshold:
                                similar_indices.append(j)
                
                # Create cluster if we have 2+ similar themes
                if len(similar_indices) >= 2:
                    for idx in similar_indices:
                        cluster_labels[idx] = cluster_id
                    cluster_id += 1
                else:
                    # Keep as individual (-1) - will create single-theme cluster
                    pass
            
            # Group themes by cluster
            clusters = {}
            individual_themes = []
            
            for idx, label in enumerate(cluster_labels):
                theme = themes[idx]
                if label == -1:
                    individual_themes.append(theme)
                else:
                    if label not in clusters:
                        clusters[label] = []
                    clusters[label].append(theme)
            
            # Create cluster objects with merged data
            theme_clusters = []
            
            # Process multi-theme clusters
            for cluster_id, cluster_themes in clusters.items():
                # Generate cluster name and description using LLM
                cluster_name, cluster_description = await self._generate_cluster_summary(cluster_themes, db)
                
                # Calculate combined stats
                combined_stats = self._calculate_cluster_stats(cluster_themes, db)
                
                theme_clusters.append({
                    "cluster_name": cluster_name,
                    "cluster_description": cluster_description,
                    "themes": cluster_themes,
                    "combined_stats": combined_stats,
                    "is_major_cluster": True
                })
            
            # Add individual themes as single-theme clusters
            for theme in individual_themes:
                theme_clusters.append({
                    "cluster_name": theme.name,
                    "cluster_description": theme.description or "",
                    "themes": [theme],
                    "combined_stats": self._calculate_cluster_stats([theme], db),
                    "is_major_cluster": False
                })
            
            # Sort by combined impact score (highest first)
            theme_clusters.sort(key=lambda c: c["combined_stats"].get("impact_score", 0), reverse=True)
            
            print(f"  ✅ Created {len(theme_clusters)} theme clusters ({len(clusters)} major clusters, {len(individual_themes)} individual themes)")
            return theme_clusters
            
        except Exception as e:
            print(f"  ❌ Error clustering themes: {str(e)}")
            import traceback
            traceback.print_exc()
            # Fallback: return themes as individual clusters
            return [{
                "cluster_name": theme.name,
                "cluster_description": theme.description or "",
                "themes": [theme],
                "combined_stats": self._calculate_cluster_stats([theme], db),
                "is_major_cluster": False
            } for theme in themes]
    
    async def _llm_cluster_themes(
        self,
        themes: List[Theme],
        db: Session
    ) -> List[Dict[str, Any]]:
        """Use LLM to intelligently cluster themes based on semantic similarity
        
        This method analyzes themes considering:
        - Theme names and descriptions
        - Sample feedback content
        - ARR impact, lost deals, competitors
        - Business context
        
        Returns a list of clusters, each containing similar themes.
        """
        if len(themes) <= 1:
            return []
        
        try:
            # Prepare theme summaries with feedback samples and business context
            theme_summaries = []
            for theme in themes:
                # Get sample feedback for context
                theme_feedback = db.query(Feedback).filter(Feedback.theme_id == theme.id).limit(5).all()
                feedback_samples = [f.content[:200] for f in theme_feedback if f.content][:5]
                
                # Get lost deal info
                lost_deal_info = {}
                if theme.extra_metadata and isinstance(theme.extra_metadata, dict):
                    lost_deal_info = theme.extra_metadata.get("lost_deal_info", {})
                
                # Build comprehensive theme summary
                theme_summary = {
                    "id": theme.id,
                    "name": theme.name,
                    "description": theme.description or "",
                    "feedback_samples": feedback_samples,
                    "request_frequency": theme.request_frequency or 0,
                    "customer_value": theme.customer_value or 0,
                    "impact_score": theme.overall_impact_score or 0,
                    "lost_deal_count": lost_deal_info.get("lost_deal_count", 0),
                    "lost_deal_arr": lost_deal_info.get("lost_deal_arr", 0),
                    "competitor_mentions": lost_deal_info.get("competitor_mentions", [])
                }
                theme_summaries.append(theme_summary)
            
            # Create prompt for LLM to cluster themes
            themes_json = []
            for ts in theme_summaries:
                themes_json.append({
                    "id": ts["id"],
                    "name": ts["name"],
                    "description": ts["description"],
                    "sample_feedback": ts["feedback_samples"][:3],  # First 3 samples
                    "request_frequency": ts["request_frequency"],
                    "customer_value": ts["customer_value"],
                    "impact_score": ts["impact_score"],
                    "lost_deals": ts["lost_deal_count"],
                    "lost_deal_arr": ts["lost_deal_arr"],
                    "competitors": ts["competitor_mentions"]
                })
            
            import json
            prompt = f"""Analyze these themes and group similar ones together into major clusters.

Themes to analyze:
{json.dumps(themes_json, indent=2)}

Group themes that are:
1. Related to the same core problem/feature area (e.g., "Export failures", "Dashboard performance", "Mobile app issues")
2. Have similar business impact (ARR, lost deals, competitors)
3. Address the same user pain points

Return JSON with this structure:
{{
  "clusters": [
    {{
      "cluster_name": "Major Cluster Name (e.g., 'Export & Data Handling Issues', 'Mobile App Performance & Stability')",
      "cluster_description": "2-3 sentence summary explaining what these themes have in common and combined impact",
      "theme_ids": [1, 5, 12]
    }}
  ]
}}

Rules:
- Only group themes that are clearly related (same problem area)
- Create descriptive cluster names like "Export Failures", "Dashboard Performance Issues", "Onboarding Complexity"
- Each theme can only be in one cluster
- If a theme doesn't fit with others, leave it unclustered (don't force it)
- Minimum 2 themes per cluster (don't create single-theme clusters)
- Focus on business impact and user pain points when grouping

Return ONLY valid JSON. No markdown, no code blocks, no explanations."""

            response = await self.llm_client.chat_completion([
                {"role": "system", "content": "You are an expert at analyzing customer feedback themes and grouping similar issues. Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ], temperature=0.3, max_tokens=2000)
            
            # Parse LLM response
            try:
                # Clean response (remove markdown if present)
                response_clean = response.strip()
                if response_clean.startswith("```json"):
                    response_clean = response_clean[7:]
                if response_clean.startswith("```"):
                    response_clean = response_clean[3:]
                if response_clean.endswith("```"):
                    response_clean = response_clean[:-3]
                response_clean = response_clean.strip()
                
                cluster_data = json.loads(response_clean)
                clusters = cluster_data.get("clusters", [])
                
                # Convert to theme clusters
                theme_clusters = []
                used_theme_ids = set()
                
                for cluster_info in clusters:
                    theme_ids = cluster_info.get("theme_ids", [])
                    if len(theme_ids) < 2:  # Skip single-theme clusters
                        continue
                    
                    # Get themes for this cluster
                    cluster_themes = [t for t in themes if t.id in theme_ids]
                    if len(cluster_themes) < 2:  # Need at least 2 themes
                        continue
                    
                    used_theme_ids.update(theme_ids)
                    theme_clusters.append({
                        "cluster_name": cluster_info.get("cluster_name", f"Cluster of {len(cluster_themes)} themes"),
                        "cluster_description": cluster_info.get("cluster_description", ""),
                        "themes": cluster_themes
                    })
                
                # Add unclustered themes as individual items (will be handled by fallback)
                if len(used_theme_ids) < len(themes):
                    # Some themes weren't clustered - they'll be handled by embedding fallback
                    print(f"  ℹ️ LLM clustered {len(used_theme_ids)}/{len(themes)} themes")
                
                return theme_clusters
                
            except json.JSONDecodeError as e:
                print(f"  ⚠️ Could not parse LLM clustering response: {str(e)}")
                print(f"  Response: {response[:500]}")
                return []
                
        except Exception as e:
            print(f"  ⚠️ Error in LLM clustering: {str(e)}")
            import traceback
            traceback.print_exc()
            return []  # Fallback to embedding-based clustering
    
    async def _generate_cluster_summary(self, themes: List[Theme], db: Session) -> Tuple[str, str]:
        """Generate cluster name and description from multiple themes using LLM
        
        Creates professional cluster names like:
        - "Export & Data Handling Issues"
        - "Mobile App Performance & Stability"
        - "Dashboard Performance Issues"
        """
        if len(themes) == 1:
            return themes[0].name, themes[0].description or ""
        
        # Get feedback samples and business context for better cluster naming
        from core.database import Feedback
        theme_details = []
        for theme in themes:
            theme_feedback = db.query(Feedback).filter(Feedback.theme_id == theme.id).limit(3).all()
            feedback_samples = [f.content[:150] for f in theme_feedback if f.content][:3]
            
            lost_deal_info = {}
            if theme.extra_metadata and isinstance(theme.extra_metadata, dict):
                lost_deal_info = theme.extra_metadata.get("lost_deal_info", {})
            
            theme_details.append({
                "name": theme.name,
                "description": theme.description or "",
                "feedback_samples": feedback_samples,
                "request_frequency": theme.request_frequency or 0,
                "impact_score": theme.overall_impact_score or 0,
                "lost_deal_count": lost_deal_info.get("lost_deal_count", 0),
                "competitor_mentions": lost_deal_info.get("competitor_mentions", [])
            })
        
        # Create detailed summary
        theme_summary = "\n\n".join([
            f"Theme: {td['name']}\n"
            f"Description: {td['description']}\n"
            f"Impact Score: {td['impact_score']:.1f}/10\n"
            f"Request Frequency: {td['request_frequency']}\n"
            f"Lost Deals: {td['lost_deal_count']}\n"
            f"Competitors: {', '.join(td['competitor_mentions']) if td['competitor_mentions'] else 'None'}\n"
            f"Sample Feedback: {'; '.join(td['feedback_samples'][:2])}"
            for td in theme_details
        ])
        
        prompt = f"""Based on these similar themes, create a professional major cluster name and summary:

{theme_summary}

Return JSON with:
- name: Professional cluster name (e.g., "Export & Data Handling Issues", "Mobile App Performance & Stability", "Dashboard Performance Issues", "Onboarding Complexity & Confusion")
- description: 2-3 sentence summary explaining:
  1. What core problem/area these themes share
  2. Combined business impact (severity, ARR, lost deals)
  3. Key personas/segments affected

Examples of good cluster names:
- "Export & Data Handling Issues" (for export failures, CSV crashes, Excel export requests)
- "Mobile App Performance & Stability" (for iOS crashes, mobile performance, offline issues)
- "Dashboard Performance Issues" (for slow loading, performance complaints)
- "Onboarding Complexity & Confusion" (for confusing setup, long onboarding)

Return ONLY valid JSON. No markdown, no code blocks, no explanations."""
        
        try:
            response = await self.llm_client.chat_completion([
                {"role": "system", "content": "You create professional theme cluster summaries. Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ], temperature=0.3, max_tokens=500)
            
            import json
            # Clean response
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            response_clean = response_clean.strip()
            
            cluster_data = json.loads(response_clean)
            cluster_name = cluster_data.get("name", f"Cluster of {len(themes)} themes")
            cluster_description = cluster_data.get("description", f"Cluster combining {len(themes)} related themes")
            return cluster_name, cluster_description
        except Exception as e:
            print(f"  ⚠️ Error generating cluster summary: {str(e)}")
            # Fallback: create descriptive name from theme names
            first_words = [t.name.split()[0] for t in themes[:3]]
            cluster_name = f"{' & '.join(set(first_words))} Issues" if first_words else f"Cluster of {len(themes)} themes"
            return cluster_name, f"Cluster combining {len(themes)} related themes addressing similar issues"
    
    def _calculate_cluster_stats(self, themes: List[Theme], db: Session) -> Dict[str, Any]:
        """Calculate combined statistics for a cluster of themes"""
        from core.database import Feedback
        
        # Aggregate all feedback from all themes in cluster
        all_feedback = []
        all_competitor_mentions = set()
        total_lost_deal_count = 0
        total_lost_deal_arr = 0
        total_arr = 0
        arr_count = 0
        total_feedback_count = 0
        pain_scores = []
        
        for theme in themes:
            theme_feedback = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
            all_feedback.extend(theme_feedback)
            total_feedback_count += theme.request_frequency or len(theme_feedback)
            
            # Get lost deal info from theme metadata
            if theme.extra_metadata and isinstance(theme.extra_metadata, dict):
                lost_deal_info = theme.extra_metadata.get("lost_deal_info", {})
                total_lost_deal_count += lost_deal_info.get("lost_deal_count", 0)
                total_lost_deal_arr += lost_deal_info.get("lost_deal_arr", 0)
                competitors = lost_deal_info.get("competitor_mentions", [])
                all_competitor_mentions.update(competitors)
            
            # Aggregate ARR
            for feedback in theme_feedback:
                if feedback.arr and feedback.arr > 0:
                    total_arr += feedback.arr
                    arr_count += 1
            
            # Collect pain scores
            if theme.customer_value:
                pain_scores.append(theme.customer_value)
        
        # Calculate averages
        avg_arr = total_arr / arr_count if arr_count > 0 else 0
        avg_pain_score = sum(pain_scores) / len(pain_scores) if pain_scores else 0
        
        # Calculate combined impact score (weighted average of theme impact scores)
        impact_scores = [t.overall_impact_score or 0 for t in themes if t.overall_impact_score]
        combined_impact_score = sum(impact_scores) / len(impact_scores) if impact_scores else 0
        
        # Determine trend (growing if any theme has positive trend velocity)
        trend_velocity = max([t.trend_velocity or 0 for t in themes])
        trend = "Growing" if trend_velocity > 0.5 else "Stable" if trend_velocity > -0.5 else "Declining"
        
        return {
            "feedback_volume": total_feedback_count,
            "avg_arr": avg_arr,
            "total_arr": total_arr,
            "lost_deal_count": total_lost_deal_count,
            "lost_deal_arr": total_lost_deal_arr,
            "competitor_mentions": list(all_competitor_mentions),
            "pain_score": avg_pain_score,
            "impact_score": combined_impact_score,
            "trend": trend,
            "trend_velocity": trend_velocity
        }

