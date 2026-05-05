---
description: Check port occupancy for common dev ports
---

Check which processes are occupying common development ports:

1. Check these ports: 3000, 5173, 5432, 8080, 8000, 3306, 6379, 27017
2. On Windows: `netstat -ano | findstr :<port>` then `tasklist | findstr <PID>`
3. On Linux/Mac: `lsof -i :<port>` or `ss -tlnp | grep <port>`
4. Report for each occupied port:
   - Port number
   - Process name and PID
   - Whether it's Docker or native process
5. If conflicts found, suggest:
   - Kill conflicting process, OR
   - Change project port config

Use this BEFORE diagnosing any "connection refused" or "port already in use" error.
