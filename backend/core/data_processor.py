from typing import Dict, List, Any, Optional
from core.agents.market_agent import MarketAgent
from core.agents.social_agent import SocialAgent
from core.agents.competitor_agent import CompetitorAgent
from core.clustering import FeedbackClustering
from core.impact_scoring import ImpactScorer
from core.database import Feedback, Document, get_db
from sqlalchemy.orm import Session
import json

class DataProcessor:
    """Main data processing orchestrator"""
    
    def __init__(self):
        self.market_agent = MarketAgent()
        self.social_agent = SocialAgent()
        self.competitor_agent = CompetitorAgent()
        self.clustering = FeedbackClustering()
        self.impact_scorer = ImpactScorer()
    
    async def process_documents(
        self,
        documents: List[Dict[str, Any]],
        db: Session
    ) -> Dict[str, Any]:
        """Process uploaded documents"""
        results = {
            "processed": 0,
            "extracted_feedback": [],
            "insights": []
        }
        
        for doc in documents:
            # Extract feedback from documents
            feedback_items = await self.extract_feedback_from_document(doc)
            results["extracted_feedback"].extend(feedback_items)
            results["processed"] += 1
        
        return results
    
    async def extract_feedback_from_document(
        self,
        document: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract feedback items from a document"""
        content = document.get("content", "")
        if not content:
            return []
        
        prompt = f"""Extract all feedback items from this document. Return JSON array where each item has:
- content: the feedback text
- type: bug, feature_request, usability_issue, integration_request, or other
- context: any relevant context

Document: {content[:3000]}
"""
        
        response = await self.market_agent.llm_client.chat_completion([
            {"role": "system", "content": "Extract feedback items from documents. Return valid JSON arrays."},
            {"role": "user", "content": prompt}
        ], temperature=0.3)
        
        try:
            return json.loads(response)
        except:
            return []
    
    async def process_feedback_batch(
        self,
        feedback_data: List[Dict[str, Any]],
        db: Session
    ) -> Dict[str, Any]:
        """Process a batch of feedback through all agents with FULL LLM/AI processing - SEMAPHORE-LIMITED PARALLEL"""
        import asyncio
        
        # Use semaphore to limit concurrent operations (faster than batching, safer than unlimited)
        # Windows has a limit of ~512 file descriptors
        # Each item makes 2 LLM calls in parallel, so MAX_CONCURRENT = 12 means max 24 file descriptors (safe)
        MAX_CONCURRENT = 12  # Process up to 12 items concurrently (24 file descriptors max with parallel calls)
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        async def process_single_item(item: Dict[str, Any]) -> Dict[str, Any]:
            """Process a single feedback item with semaphore-controlled concurrency"""
            async with semaphore:  # Limit concurrent operations
                try:
                    # Run classification and metadata extraction in PARALLEL for speed
                    # Semaphore ensures we don't exceed file descriptor limits
                    classification_task = self.market_agent.classify_feedback(
                        item.get("content", ""),
                        item.get("context", {})
                    )
                    metadata_task = self.market_agent.extract_metadata(
                        item.get("content", ""),
                        item.get("source", "unknown")
                    )
                    
                    # Wait for both to complete in parallel (faster!)
                    classification, metadata = await asyncio.gather(
                        classification_task, 
                        metadata_task,
                        return_exceptions=True
                    )
                    
                    # Handle exceptions
                    if isinstance(classification, Exception):
                        print(f"⚠️ Classification error for item: {str(classification)}")
                        classification = {
                            "classification": "feature_request",
                            "sentiment_score": 0.0,
                            "pain_level": 5.0,
                            "urgency": "medium",
                            "feature": None,
                            "reason": "Error during classification"
                        }
                    
                    if isinstance(metadata, Exception):
                        print(f"⚠️ Metadata extraction error for item: {str(metadata)}")
                        metadata = {
                            "user_segment": None,
                            "account_id": item.get("account_id"),
                            "arr": item.get("arr", 0),
                            "churn_risk": 0.5,
                            "additional_metadata": {}
                        }
                    
                    return {
                        "item": item,
                        "classification": classification,
                        "metadata": metadata
                    }
                except Exception as e:
                    print(f"❌ Error processing item: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    # Return fallback data so processing can continue
                    return {
                        "item": item,
                        "classification": {
                            "classification": "feature_request",
                            "sentiment_score": 0.0,
                            "pain_level": 5.0,
                            "urgency": "medium",
                            "feature": None,
                            "reason": f"Error: {str(e)}"
                        },
                        "metadata": {
                            "user_segment": None,
                            "account_id": item.get("account_id"),
                            "arr": item.get("arr", 0),
                            "churn_risk": 0.5,
                            "additional_metadata": {}
                        }
                    }
        
        # Process all items concurrently with semaphore limiting
        print(f"🚀 Processing {len(feedback_data)} items with MAX {MAX_CONCURRENT} concurrent (semaphore-controlled)...")
        processed_items = []
        
        # Process in smaller batches with progress tracking to avoid hanging
        BATCH_SIZE = 50  # Process 50 items at a time to show progress (larger batches = faster)
        total_batches = (len(feedback_data) + BATCH_SIZE - 1) // BATCH_SIZE
        
        for batch_num in range(total_batches):
            start_idx = batch_num * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(feedback_data))
            batch = feedback_data[start_idx:end_idx]
            
            print(f"  📦 Processing batch {batch_num + 1}/{total_batches} (items {start_idx + 1}-{end_idx})...")
            
            # Create tasks for this batch
            tasks = [process_single_item(item) for item in batch]
            
            # Process batch with timeout to prevent hanging
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=180.0  # 3 minute timeout per batch (larger batches need more time)
                )
            except asyncio.TimeoutError:
                print(f"  ⚠️ Batch {batch_num + 1} timed out after 2 minutes, creating fallback results...")
                results = []
                for item in batch:
                    results.append({
                        "item": item,
                        "classification": {
                            "classification": "feature_request",
                            "sentiment_score": 0.0,
                            "pain_level": 5.0,
                            "urgency": "medium",
                            "feature": None,
                            "reason": "Processing timeout"
                        },
                        "metadata": {
                            "user_segment": None,
                            "account_id": item.get("account_id"),
                            "arr": item.get("arr", 0),
                            "churn_risk": 0.5,
                            "additional_metadata": {}
                        }
                    })
            
            # Filter out exceptions and collect valid results
            for idx, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"  ❌ Error processing item {start_idx + idx}: {str(result)}")
                    # Create fallback result
                    processed_items.append({
                        "item": batch[idx],
                        "classification": {
                            "classification": "feature_request",
                            "sentiment_score": 0.0,
                            "pain_level": 5.0,
                            "urgency": "medium",
                            "feature": None,
                            "reason": f"Error: {str(result)}"
                        },
                        "metadata": {
                            "user_segment": None,
                            "account_id": batch[idx].get("account_id"),
                            "arr": batch[idx].get("arr", 0),
                            "churn_risk": 0.5,
                            "additional_metadata": {}
                        }
                    })
                else:
                    processed_items.append(result)
            
            print(f"  ✅ Batch {batch_num + 1} complete: {len([r for r in results if not isinstance(r, Exception)])}/{len(batch)} items succeeded")
        
        print(f"  ✅ Total: Processed {len(processed_items)}/{len(feedback_data)} items successfully")
        
        # Create feedback objects from processed items
        # Filter out items with empty content before processing
        feedback_objects = []
        for result in processed_items:
            item = result["item"]
            classification = result["classification"]
            metadata = result["metadata"]
            
            # Skip items with empty content
            content = item.get("content", "").strip()
            if not content:
                print(f"⚠️ Skipping feedback item with empty content from source: {item.get('source', 'unknown')}")
                continue
            
            # Parse created_at date from item
            created_at = None
            if item.get("created_at"):
                try:
                    from datetime import datetime
                    created_at_str = item.get("created_at")
                    # Handle ISO format with or without timezone
                    if isinstance(created_at_str, str):
                        # Remove timezone if present
                        if 'T' in created_at_str:
                            # ISO format: 2025-07-10T11:00:00Z or 2025-07-10T11:00:00+00:00
                            created_at_str = created_at_str.split('+')[0].split('Z')[0].split('.')[0]
                            created_at = datetime.fromisoformat(created_at_str)
                        else:
                            # Date only: 2025-07-10
                            created_at = datetime.fromisoformat(created_at_str)
                        # Ensure it's naive (no timezone)
                        if created_at.tzinfo is not None:
                            created_at = created_at.replace(tzinfo=None)
                    elif isinstance(created_at_str, datetime):
                        created_at = created_at_str
                        if created_at.tzinfo is not None:
                            created_at = created_at.replace(tzinfo=None)
                except Exception as e:
                    print(f"⚠️ Error parsing created_at date '{item.get('created_at')}': {e}, using current time")
                    created_at = None
            
            feedback = Feedback(
                source=item.get("source", "unknown"),
                source_id=item.get("source_id"),
                content=content,
                classification=classification.get("classification"),
                sentiment_score=classification.get("sentiment_score", 0.0),
                pain_level=classification.get("pain_level", 0.0),
                urgency=classification.get("urgency", "medium"),
                feature=classification.get("feature"),
                reason=classification.get("reason"),
                user_segment=metadata.get("user_segment"),
                account_id=metadata.get("account_id"),
                arr=metadata.get("arr"),
                churn_risk=metadata.get("churn_risk", 0.5),
                extra_metadata=metadata.get("additional_metadata", {}),
                created_at=created_at  # Set the parsed date
            )
            feedback_objects.append(feedback)
        
        # Batch commit all feedback at once (faster than individual commits)
        if feedback_objects:
            try:
                db.add_all(feedback_objects)
                db.commit()
                
                # Refresh to get IDs
                processed_feedback = []
                for feedback in feedback_objects:
                    try:
                        db.refresh(feedback)
                        processed_feedback.append({
                            "id": feedback.id,
                            "content": feedback.content,
                            "classification": feedback.classification,
                            "sentiment_score": feedback.sentiment_score,
                            "pain_level": feedback.pain_level,
                            "created_at": feedback.created_at  # Include date for quarter-aware clustering
                        })
                    except Exception as refresh_error:
                        print(f"⚠️ Error refreshing feedback ID: {str(refresh_error)}")
                        # Use the object directly if refresh fails
                        if hasattr(feedback, 'id') and feedback.id:
                            processed_feedback.append({
                                "id": feedback.id,
                                "content": feedback.content,
                                "classification": feedback.classification,
                                "sentiment_score": feedback.sentiment_score,
                                "pain_level": feedback.pain_level,
                                "created_at": feedback.created_at  # Include date for quarter-aware clustering
                            })
            except Exception as commit_error:
                print(f"❌ Error committing feedback: {str(commit_error)}")
                db.rollback()
                # Try to commit items one by one as fallback
                processed_feedback = []
                for feedback in feedback_objects:
                    try:
                        db.add(feedback)
                        db.commit()
                        db.refresh(feedback)
                        processed_feedback.append({
                            "id": feedback.id,
                            "content": feedback.content,
                            "classification": feedback.classification,
                            "sentiment_score": feedback.sentiment_score,
                            "pain_level": feedback.pain_level,
                            "created_at": feedback.created_at  # Include date for quarter-aware clustering
                        })
                    except Exception as single_error:
                        print(f"⚠️ Error committing single feedback item: {str(single_error)}")
                        db.rollback()
                        continue
        else:
            processed_feedback = []
        
        # Cluster feedback using REAL embeddings and LLM
        # Themes are created with impact scores calculated IMMEDIATELY (no 0.0)
        print(f"  🔄 Clustering {len(processed_feedback)} feedback items together...")
        print(f"     This will group similar requests from all sources into themes")
        try:
            themes = await self.clustering.cluster_feedback(processed_feedback, db)
            print(f"  ✅ Clustering complete: {len(themes)} themes created")
            
            # Post-process: Only merge themes if they're VERY similar using embeddings
            # Disabled aggressive keyword-based merging as it was merging unrelated themes
            # The initial clustering with threshold 0.80 should already group similar items correctly
            if len(themes) > 1:
                print(f"  🔄 Post-processing: Checking for very similar themes to merge (using embeddings)...")
                from core.database import Theme
                all_themes = db.query(Theme).order_by(Theme.created_at.desc()).limit(20).all()  # Only check recent themes
                if len(all_themes) > 1:
                    # Use embeddings to find truly similar themes (much more accurate than keywords)
                    try:
                        from core.clustering import FeedbackClustering
                        clustering_helper = FeedbackClustering()
                        
                        # Get sample content from each theme
                        theme_samples = []
                        theme_ids = []
                        for theme in all_themes:
                            theme_feedback = db.query(Feedback).filter(Feedback.theme_id == theme.id).limit(3).all()
                            if theme_feedback:
                                sample_text = f"{theme.name} {theme.description or ''} " + " ".join([f.content[:200] for f in theme_feedback[:3]])
                                theme_samples.append(sample_text)
                                theme_ids.append(theme.id)
                        
                        if len(theme_samples) > 1:
                            # Get embeddings for theme samples
                            theme_embeddings = await clustering_helper.llm_client.embeddings(theme_samples)
                            
                            # Find very similar themes (threshold 0.85 - very high to avoid false merges)
                            merged_count = 0
                            themes_to_delete = []
                            import numpy as np
                            
                            for i, (theme1_id, theme1_emb) in enumerate(zip(theme_ids, theme_embeddings)):
                                if theme1_id in themes_to_delete:
                                    continue
                                
                                theme1 = db.query(Theme).filter(Theme.id == theme1_id).first()
                                if not theme1:
                                    continue
                                
                                for j, (theme2_id, theme2_emb) in enumerate(zip(theme_ids[i+1:], theme_embeddings[i+1:]), start=i+1):
                                    if theme2_id in themes_to_delete or theme2_id == theme1_id:
                                        continue
                                    
                                    # Calculate cosine similarity
                                    dot_product = np.dot(theme1_emb, theme2_emb)
                                    norm1 = np.linalg.norm(theme1_emb)
                                    norm2 = np.linalg.norm(theme2_emb)
                                    if norm1 > 0 and norm2 > 0:
                                        similarity = dot_product / (norm1 * norm2)
                                        
                                        # Only merge if VERY similar (0.85 threshold - very high)
                                        if similarity >= 0.85:
                                            theme2 = db.query(Theme).filter(Theme.id == theme2_id).first()
                                            if theme2:
                                                theme2_feedback = db.query(Feedback).filter(Feedback.theme_id == theme2_id).all()
                                                theme1_feedback = db.query(Feedback).filter(Feedback.theme_id == theme1_id).all()
                                                
                                                print(f"  🔍 Found very similar themes: '{theme1.name}' and '{theme2.name}' (similarity: {similarity:.3f})")
                                                print(f"  🔗 Merging: '{theme2.name}' ({len(theme2_feedback)} items) into '{theme1.name}' ({len(theme1_feedback)} items)")
                                                
                                                # Merge theme2 into theme1
                                                for feedback in theme2_feedback:
                                                    feedback.theme_id = theme1.id
                                                
                                                # Update theme1 stats
                                                all_theme1_feedback = db.query(Feedback).filter(Feedback.theme_id == theme1_id).all()
                                                theme1.request_frequency = len(all_theme1_feedback)
                                                
                                                # Mark theme2 for deletion
                                                themes_to_delete.append(theme2_id)
                                                merged_count += 1
                                                break  # Don't check more themes for theme1
                            
                            # Delete merged themes
                            if themes_to_delete:
                                for theme_id in themes_to_delete:
                                    theme_to_delete = db.query(Theme).filter(Theme.id == theme_id).first()
                                    if theme_to_delete:
                                        db.delete(theme_to_delete)
                                db.commit()
                                if merged_count > 0:
                                    print(f"  ✅ Merged {merged_count} very similar themes together (using embeddings)")
                    except Exception as e:
                        print(f"  ⚠️ Post-processing merge failed (non-critical): {str(e)}")
                        # Continue without merging - initial clustering should be sufficient
        except Exception as e:
            print(f"  ❌ Error in clustering feedback: {str(e)}")
            import traceback
            traceback.print_exc()
            themes = []  # Continue even if clustering fails
        
        # Update request_frequency for all themes to reflect actual feedback count
        from core.database import Theme
        all_themes = db.query(Theme).all()
        for theme in all_themes:
            actual_count = db.query(Feedback).filter(Feedback.theme_id == theme.id).count()
            if actual_count != theme.request_frequency:
                theme.request_frequency = actual_count
                print(f"  📊 Updated theme '{theme.name}': request_frequency = {actual_count} (was {theme.request_frequency})")
        
        # Double-check: Recalculate impact scores to ensure accuracy
        # (Themes already have scores from clustering, but this ensures everything is perfect)
        await self.impact_scorer.update_theme_impact_scores(db)
        db.commit()
        
        print(f"  ✅ Final theme counts: {[(t.name, db.query(Feedback).filter(Feedback.theme_id == t.id).count()) for t in all_themes]}")
        
        # AUTOMATICALLY GENERATE RECOMMENDATIONS WITH FULL DETAILS after themes are created
        if len(all_themes) > 0:
            print(f"\n🚀 Automatically generating recommendations with FULL details for {len(all_themes)} themes...")
            try:
                from core.roadmap_generator import RoadmapGenerator
                from core.database import Recommendation, Competitor
                roadmap_generator = RoadmapGenerator()
                
                # Get competitor insights
                competitors = db.query(Competitor).all()
                competitor_insights = {
                    "competitors": [
                        {
                            "name": c.name,
                            "strengths": c.strengths,
                            "weaknesses": c.weaknesses,
                            "opportunities": c.opportunities
                        }
                        for c in competitors
                    ],
                    "market_gaps": [c.market_gaps for c in competitors if c.market_gaps],
                    "opportunities": [c.opportunities for c in competitors if c.opportunities]
                }
                
                # Group themes by quarter based on their feedback dates
                # This ensures recommendations are quarter-specific
                from datetime import datetime
                from collections import defaultdict
                themes_by_quarter = defaultdict(list)
                
                for theme in all_themes:
                    # Get feedback for this theme to determine its quarter
                    theme_feedback = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
                    if not theme_feedback:
                        continue
                    
                    # Determine quarter from feedback dates
                    feedback_dates = [f.created_at for f in theme_feedback if f.created_at]
                    if not feedback_dates:
                        continue
                    
                    # Use the most common quarter from feedback dates
                    quarter_counts = defaultdict(int)
                    for date in feedback_dates:
                        if date:
                            year = date.year
                            month = date.month
                            if month <= 3:
                                quarter = f"Q1_{year}"
                            elif month <= 6:
                                quarter = f"Q2_{year}"
                            elif month <= 9:
                                quarter = f"Q3_{year}"
                            else:
                                quarter = f"Q4_{year}"
                            quarter_counts[quarter] += 1
                    
                    if quarter_counts:
                        # Assign theme to the quarter with most feedback
                        theme_quarter = max(quarter_counts.items(), key=lambda x: x[1])[0]
                        themes_by_quarter[theme_quarter].append(theme)
                
                # Generate recommendations for each quarter separately
                recommendations_created = 0
                for quarter_key, quarter_themes in themes_by_quarter.items():
                    # Get top themes by impact score for this quarter
                    top_themes = sorted(quarter_themes, key=lambda t: t.overall_impact_score, reverse=True)[:15]
                    
                    # Parse quarter and year
                    quarter, year_str = quarter_key.split('_')
                    year = int(year_str)
                    
                    print(f"  📅 Generating recommendations for {quarter} {year}: {len(top_themes)} themes")
                    
                    for idx, theme in enumerate(top_themes):
                        try:
                            # Check if recommendation already exists for this quarter
                            existing = db.query(Recommendation).filter(
                                Recommendation.feature == theme.name,
                                Recommendation.created_at >= datetime(year, 1 if quarter == 'Q1' else (4 if quarter == 'Q2' else (7 if quarter == 'Q3' else 10)), 1),
                                Recommendation.created_at < datetime(year + 1 if quarter == 'Q4' else year, (4 if quarter == 'Q1' else (7 if quarter == 'Q2' else (10 if quarter == 'Q3' else 1))), 1)
                            ).first()
                            if existing:
                                print(f"  [{idx+1}/{len(top_themes)}] Recommendation already exists for: {theme.name} ({quarter} {year})")
                                continue
                            
                            print(f"  [{idx+1}/{len(top_themes)}] Creating recommendation for: {theme.name} (Impact: {theme.overall_impact_score}/10) - {quarter} {year}")
                            
                            # Get feedback for this theme
                            theme_feedback = db.query(Feedback).filter(Feedback.theme_id == theme.id).all()
                            
                            # Prepare full theme data
                            theme_data_dict = {
                                "id": theme.id,
                                "name": theme.name,
                                "description": theme.description,
                                "impact_score": theme.overall_impact_score,
                                "customer_value": theme.customer_value,
                                "request_frequency": theme.request_frequency,
                                "feedback_count": len(theme_feedback),
                                "extra_metadata": theme.extra_metadata or {}
                            }
                            
                            # Create recommendation from theme (with LLM)
                            recommendation_data = await roadmap_generator.create_recommendation_from_theme(
                                theme_data_dict,
                                competitor_insights,
                                db
                            )
                            
                            # Run FULL persona agent deliberation with competitor data, lost deals, etc.
                            deliberation = await roadmap_generator.deliberation_system.deliberate(
                                recommendation_data,
                                {
                                    "theme": theme_data_dict,
                                    "competitor_insights": competitor_insights
                                }
                            )
                            
                            # Extract customer quotes
                            customer_quotes = await roadmap_generator.extract_customer_quotes(theme.id, db)
                            
                            # Get data justification (includes strategic_rationale, customer_demand, prioritization_recommendation)
                            from core.impact_scoring import ImpactScorer
                            impact_scorer = ImpactScorer()
                            data_justification = await impact_scorer.get_data_justification_for_theme(theme.id, db)
                            
                            # Determine created_at date based on quarter (use middle of quarter)
                            if quarter == 'Q1':
                                rec_created_at = datetime(year, 2, 15)  # Mid-February
                            elif quarter == 'Q2':
                                rec_created_at = datetime(year, 5, 15)  # Mid-May
                            elif quarter == 'Q3':
                                rec_created_at = datetime(year, 8, 15)  # Mid-August
                            else:  # Q4
                                rec_created_at = datetime(year, 11, 15)  # Mid-November
                            
                            # Get existing extra_metadata if any
                            existing_metadata = recommendation_data.get("extra_metadata", {}) or {}
                            
                            # Create recommendation with FULL evidence
                            recommendation = Recommendation(
                                title=recommendation_data.get("title", f"Enhance {theme.name}"),
                                description=recommendation_data.get("description", theme.description),
                                feature=theme.name,
                                impact_score=theme.overall_impact_score,
                                feasibility_score=deliberation["evaluations"]["engineering"].get("feasibility_score", 5.0),
                                risk_score=deliberation["evaluations"]["engineering"].get("risk_score", 5.0),
                                ux_implications=deliberation["evaluations"]["ux"].get("ux_implications", ""),
                                business_impact=deliberation["evaluations"]["pm"].get("business_impact", ""),
                                pm_verdict=deliberation["evaluations"]["pm"].get("reasoning", ""),
                                ux_verdict=deliberation["evaluations"]["ux"].get("reasoning", ""),
                                data_scientist_verdict=deliberation["evaluations"]["data_scientist"].get("reasoning", ""),
                                engineering_verdict=deliberation["evaluations"]["engineering"].get("reasoning", ""),
                                unified_recommendation=deliberation["unified_recommendation"].get("unified_reasoning", ""),
                                customer_quotes=customer_quotes,
                                evidence={
                                    **deliberation,  # Includes evaluations, unified_recommendation with team_discussion, key_debate_points, action_items
                                    "data_justification": data_justification  # Includes strategic_rationale, customer_demand, prioritization_recommendation
                                },
                                status="pending",
                                created_at=rec_created_at,  # Set quarter-specific date
                                extra_metadata={
                                    **existing_metadata,
                                    "quarter": quarter,
                                    "year": year
                                }
                            )
                            
                            db.add(recommendation)
                            db.commit()
                            db.refresh(recommendation)
                            recommendations_created += 1
                            
                            print(f"    ✅ Created: {recommendation.title}")
                            print(f"       - Team Discussion: {'✅' if deliberation.get('unified_recommendation', {}).get('team_discussion') else '❌'}")
                            print(f"       - Debate Points: {'✅' if deliberation.get('unified_recommendation', {}).get('key_debate_points') else '❌'}")
                            print(f"       - Action Items: {'✅' if deliberation.get('unified_recommendation', {}).get('action_items') else '❌'}")
                            print(f"       - Data Justification: {'✅' if data_justification else '❌'}")
                        except Exception as rec_error:
                            print(f"  ⚠️ Error creating recommendation for {theme.name}: {str(rec_error)}")
                            import traceback
                            traceback.print_exc()
                            continue
                        continue
                
                print(f"\n✅ Automatically created {recommendations_created} recommendations with FULL details!")
                print(f"   All recommendations include:")
                print(f"   - Team Evaluations (PM, UX, Data Scientist, Engineering)")
                print(f"   - Key Debate Points")
                print(f"   - Detailed Reasoning")
                print(f"   - Next Steps & Action Items")
                print(f"   - Implementation Guidance")
                print(f"   - Professional Summary")
                print(f"   - Revenue Impact")
                
            except Exception as e:
                print(f"  ⚠️ Error automatically generating recommendations: {str(e)}")
                import traceback
                traceback.print_exc()
                # Continue - recommendations can be generated manually later
        
        return {
            "processed_count": len(processed_feedback),
            "themes_created": len(themes),
            "feedback": processed_feedback
        }
    
    async def run_full_analysis(
        self,
        product_info: Dict[str, Any],
        feedback_data: List[Dict[str, Any]],
        social_data: List[Dict[str, Any]],
        documents: List[Dict[str, Any]],
        db: Session
    ) -> Dict[str, Any]:
        """Run full end-to-end analysis"""
        results = {
            "market_analysis": {},
            "social_analysis": {},
            "competitor_analysis": {},
            "themes": [],
            "recommendations": []
        }
        
        # Process feedback
        feedback_results = await self.process_feedback_batch(feedback_data, db)
        
        # Market agent analysis
        market_data = {
            "feedback": feedback_data,
            "documents": documents
        }
        results["market_analysis"] = await self.market_agent.analyze(market_data)
        
        # Social agent analysis
        social_agent_data = {
            "social_data": social_data,
            "reviews": [f for f in feedback_data if f.get("source") in ["app_store", "review"]],
            "forum_posts": [f for f in feedback_data if f.get("source") == "forum"]
        }
        results["social_analysis"] = await self.social_agent.analyze(social_agent_data)
        
        # Competitor agent analysis
        competitor_data = {
            "product_info": product_info,
            "market_context": {
                "feedback_themes": [t.get("name") for t in feedback_results.get("themes", [])],
                "market_insights": results["market_analysis"].get("insights", [])
            }
        }
        results["competitor_analysis"] = await self.competitor_agent.analyze(competitor_data)
        
        # Get themes
        themes = db.query(Theme).order_by(Theme.overall_impact_score.desc()).limit(20).all()
        results["themes"] = [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "impact_score": t.overall_impact_score,
                "request_frequency": t.request_frequency,
                "customer_value": t.customer_value
            }
            for t in themes
        ]
        
        return results

