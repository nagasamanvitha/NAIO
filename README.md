# NAIO

To start n8n : 
n8n\start_n8n_direct.bat  


To start backend  : 

cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8002	

To start frontend :

cd frontend
npm install
npm run dev	
