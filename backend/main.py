from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from typing import List, Optional
import os
from dotenv import load_dotenv
import traceback

from api.routes import agents, documents, dashboard, feedback, competitor, roadmap, feedback_loop, mock_data, demo, recommendations, n8n_webhooks, n8n_trigger, trends, customer_notifications, adoption, quarterly_reports
from api.routes import generate_full_recommendations
from core.database import init_db
from core.websocket_manager import ConnectionManager

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - initialize database (NO AUTO-GENERATED MOCK DATA)
    init_db()
    
    # Check database status (but don't auto-generate mock data)
    from core.database import get_db, Feedback, Theme, Recommendation
    
    try:
        db = next(get_db())
        feedback_count = db.query(Feedback).count()
        themes_count = db.query(Theme).count()
        recommendations_count = db.query(Recommendation).count()
        
        if feedback_count == 0:
            print("Database is empty. Waiting for n8n workflow data...")
            print("Execute your n8n workflow to send data to the backend.")
        else:
            print(f"Database has {feedback_count} feedback items, {themes_count} themes, and {recommendations_count} recommendations")
            print("(Using real data from n8n workflows)")
        
        db.close()
    except Exception as e:
        print(f"Error checking database: {e}")
        import traceback
        traceback.print_exc()
    
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Multi-Agent Intelligence System",
    description="Competitor, Market, and Social intelligence analysis platform",
    version="1.0.0",
    lifespan=lifespan
)

# Global exception handler to catch all unhandled exceptions (except HTTPException)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and return proper JSON response"""
    # Don't override HTTPException - let FastAPI handle those
    if isinstance(exc, HTTPException):
        raise exc
    
    import traceback
    error_trace = traceback.format_exc()
    print(f"❌ Unhandled exception: {str(exc)}")
    print(f"❌ Full traceback:\n{error_trace}")
    
    # Return JSON response - use 200 for webhook endpoints so n8n doesn't fail
    # Check if this is a webhook endpoint
    is_webhook = "/api/n8n" in str(request.url.path)
    status_code = 200 if is_webhook else 500
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": f"Internal server error: {str(exc)}",
            "error_type": type(exc).__name__,
            "error_details": error_trace[:1000] if len(error_trace) > 1000 else error_trace,
            "path": str(request.url.path)
        }
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager
manager = ConnectionManager()

# Include routers
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
app.include_router(competitor.router, prefix="/api/competitor", tags=["competitor"])
app.include_router(roadmap.router, prefix="/api/roadmap", tags=["roadmap"])
app.include_router(quarterly_reports.router, prefix="/api/quarterly-reports", tags=["quarterly-reports"])
app.include_router(feedback_loop.router, prefix="/api/feedback-loop", tags=["feedback-loop"])
app.include_router(mock_data.router, prefix="/api/mock-data", tags=["mock-data"])
app.include_router(demo.router, prefix="/api/demo", tags=["demo"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(n8n_webhooks.router, prefix="/api/n8n", tags=["n8n"])
app.include_router(n8n_trigger.router, prefix="/api/n8n", tags=["n8n"])
app.include_router(trends.router, prefix="/api/trends", tags=["trends"])
app.include_router(customer_notifications.router, prefix="/api/customer-notifications", tags=["customer-notifications"])
app.include_router(adoption.router, prefix="/api/adoption", tags=["adoption"])
app.include_router(generate_full_recommendations.router, prefix="/api/recommendations", tags=["recommendations"])

@app.get("/")
async def root():
    return {"message": "Multi-Agent Intelligence System API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/test-error")
async def test_error():
    """Test endpoint to verify exception handler works"""
    raise Exception("Test error - this should be caught by global handler")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

