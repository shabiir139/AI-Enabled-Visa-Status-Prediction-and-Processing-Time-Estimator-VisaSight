#!/bin/bash

echo "========================================="
echo "   VisaSight Automated Startup"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Step 1: Verify files
echo -e "${CYAN}[1/4] Verifying required files...${NC}"
if [ -f "frontend/src/app/layout.tsx" ] && [ -f "frontend/src/app/page.tsx" ] && [ -f "frontend/src/app/error.tsx" ]; then
    echo -e "${GREEN}✓ All required files present${NC}"
else
    echo -e "${YELLOW}⚠ Some files may be missing${NC}"
fi

# Step 2: Clear caches
echo -e "\n${CYAN}[2/4] Clearing build caches...${NC}"
rm -rf frontend/.next 2>/dev/null
rm -rf frontend/node_modules/.cache 2>/dev/null
echo -e "${GREEN}✓ Caches cleared${NC}"

# Step 3: Check if backend is running
echo -e "\n${CYAN}[3/4] Checking backend status...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running on port 8000${NC}"
else
    echo -e "${YELLOW}⚠ Backend not detected. Start it with:${NC}"
    echo -e "   cd backend && python -m uvicorn main:app --reload --port 8000"
fi

# Step 4: Frontend status
echo -e "\n${CYAN}[4/4] Checking frontend...${NC}"
if nc -z localhost 3000 2>/dev/null; then
    echo -e "${GREEN}✓ Frontend is running on port 3000${NC}"
    echo -e "\n${YELLOW}⚠ Frontend needs restart to apply fixes${NC}"
    echo -e "   1. Stop frontend terminal (Ctrl+C)"
    echo -e "   2. Run: npm run dev"
    echo -e "   3. Visit: http://localhost:3000"
else
    echo -e "${YELLOW}⚠ Frontend not detected. Start it with:${NC}"
    echo -e "   cd frontend && npm run dev"
fi

echo -e "\n========================================="
echo -e "${GREEN}Setup complete!${NC}"
echo -e "========================================="
echo -e "\nNext steps:"
echo -e "1. Restart frontend terminal (Ctrl+C, then 'npm run dev')"
echo -e "2. Open: ${CYAN}http://localhost:3000${NC}"
echo -e "3. Press: ${YELLOW}Ctrl+Shift+F5${NC} to force refresh"
echo ""
