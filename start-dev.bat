@echo off
echo Starting both frontend and backend development servers...

echo.
echo Starting frontend development server...
start "Frontend Dev Server" cmd /k "cd frontend && npm run dev"

echo.
echo Starting backend development server...
start "Backend Dev Server" cmd /k "cd backend && set GEMINI_API_KEY=placeholder && python -m langgraph_cli dev --allow-blocking"

echo.
echo Development servers are starting...
echo Frontend: http://localhost:5173/app/
echo Backend API: http://127.0.0.1:2024
echo LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
echo.
echo Press any key to exit...
pause 