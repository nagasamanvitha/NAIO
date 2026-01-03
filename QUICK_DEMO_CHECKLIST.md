# Quick Demo Checklist

## ✅ Pre-Demo Setup (5 minutes before)

- [ ] Start backend: `START_BACKEND.bat` or `cd backend && uvicorn main:app --reload --host 127.0.0.1 --port 8002`
- [ ] Start frontend: `START_FRONTEND.bat` or `cd frontend && npm run dev`
- [ ] Wait 30 seconds for services to start
- [ ] Open browser: http://localhost:3000
- [ ] Verify backend: http://localhost:8002/docs (should show Swagger UI)
- [ ] Check if data exists (if not, run n8n workflow or use mock data)
- [ ] Close unnecessary tabs/windows
- [ ] Have demo script open or memorized

## 🎯 Demo Flow (5 minutes)

### Minute 1: Introduction + Feedback Inbox
- [ ] Introduce the problem (fragmented feedback)
- [ ] Show Feedback Inbox page
- [ ] Demonstrate filters
- [ ] Point out sentiment analysis and pain scores

### Minute 2: Themes & Impact Scoring
- [ ] Navigate to Themes page
- [ ] Show theme cards with metrics
- [ ] Open a theme to show clustered feedback
- [ ] Navigate to Impact Scoring
- [ ] Explain scoring formula

### Minute 3: AI Roadmap + Features
- [ ] Navigate to AI Roadmap
- [ ] Show quarterly proposal
- [ ] Open a feature recommendation
- [ ] Navigate to Features page
- [ ] Show multi-agent evaluations

### Minute 4: Reports + Competitors
- [ ] Navigate to Quarterly Reports
- [ ] Show Q4 2025 summary
- [ ] Navigate to Competitor Radar
- [ ] Highlight competitive intelligence

### Minute 5: Technical + Conclusion
- [ ] Show API documentation (optional)
- [ ] Summarize key metrics
- [ ] Highlight GenAI innovation
- [ ] Conclude with business impact

## 🚨 Troubleshooting

**If backend won't start:**
- Check if port 8002 is available
- Verify `.env` file has `OPENROUTER_API_KEY`
- Check Python virtual environment is activated

**If frontend won't start:**
- Check if port 3000 is available
- Verify `npm install` was run
- Check Node.js version (needs 18+)

**If no data showing:**
- Run n8n workflow to send data
- Or use mock data endpoints
- Check browser console for errors

**If API errors:**
- Verify OpenRouter API key is valid
- Check backend logs for errors
- Ensure backend is running on port 8002

## 💡 Quick Tips

1. **Practice once** before the actual demo
2. **Have backup plan** - if something breaks, show screenshots from PDF
3. **Keep it simple** - focus on features, not technical details
4. **Show metrics** - always point out the 92.3% accuracy, $3.08M ARR
5. **Emphasize AI** - this is a GenAI project, highlight that
6. **Be confident** - you built a working system!

## 📊 Key Numbers to Mention

- **92.3%** classification accuracy
- **87.1%** sentiment accuracy  
- **$3.08M** ARR at risk
- **21** lost deals
- **300+** feedback items processed
- **8** data sources integrated
- **5 minutes** processing time
- **100%** feedback coverage

Good luck! 🎉

