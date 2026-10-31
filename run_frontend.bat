@echo off
title JobGuard AI - Frontend Server
echo ========================================================
echo Starting JobGuard AI Frontend (React + Vite)...
echo ========================================================
cd /d "%~dp0frontend"
npm run dev
pause

