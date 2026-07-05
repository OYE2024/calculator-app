# Quick Start Guide - Online Calculator

## ⚡ 5-Minute Local Setup

### Step 1: Create Project Structure

```bash
# Create project directory
mkdir calculator-app && cd calculator-app

# Create subdirectories
mkdir templates static .ebextensions
```

### Step 2: Copy Files to Correct Locations

Place the provided files in these locations:

```
calculator-app/
├── app.py                          (root)
├── requirements.txt                (root)
├── Dockerfile                      (root)
├── docker-compose.yml              (root)
├── README.md                       (root)
├── DEPLOYMENT_GUIDE.md             (root)
├── QUICKSTART.md                   (root)
├── .gitignore                      (root)
├── .ebignore                       (root)
├── .env.example                    (root)
├── templates/
│   └── index.html                  (rename from templates_index.html)
├── static/                         (empty, for CSS/JS if needed)
└── .ebextensions/
    ├── 01_python.config            (from ebextensions_01_python.config)
    ├── 02_rds.config               (from ebextensions_02_rds.config)
    └── 03_healthcheck.config       (from ebextensions_03_healthcheck.config)
```

### Step 3: Install Dependencies (Local Development)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 4: Run Locally with Docker

```bash
# Build and start containers
docker-compose up -d

# Check status
docker-compose ps

# Access application
# Open browser: http://localhost:5000
```

### Step 5: Test Application

```bash
# Test health check
curl http://localhost:5000/health

# Test calculation (in terminal)
curl -X POST http://localhost:5000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": "2 + 2"}'

# Expected response:
# {"expression": "2 + 2", "result": 4, "id": 1}
```

### Step 6: Stop Local Environment

```bash
docker-compose down
```

---

## 🚀 30-Minute AWS Deployment

### Prerequisites

```bash
# Install AWS CLI
pip install awscli

# Install EB CLI
pip install awsebcli

# Configure AWS (you'll need AWS credentials)
aws configure
# Enter your Access Key ID, Secret Access Key, and region (us-east-1)
```

### Step 1: Initialize Elastic Beanstalk

```bash
# In calculator-app directory
eb init -p python-3.11 calculator-app --region us-east-1
```

### Step 2: Create Environment

```bash
# Create development environment
eb create calculator-dev --instance-type t3.micro

# This takes 5-10 minutes
# Watch progress:
eb events --follow
```

### Step 3: Set Database Password

```bash
# After environment is created, set the database password
eb setenv RDS_PASSWORD=YourSecurePassword123!
```

### Step 4: Deploy Application

```bash
# Deploy the application
eb deploy

# Check status
eb status
```

### Step 5: Access Application

```bash
# Open in browser
eb open

# Or get the URL
eb status | grep "CNAME"
```

---

## 📝 File Renaming Guide

When you download the files, some need to be renamed:

| Original Name | New Location | Instructions |
|---------------|--------------|--------------|
| `templates_index.html` | `templates/index.html` | Move to templates folder |
| `ebextensions_01_python.config` | `.ebextensions/01_python.config` | Move to .ebextensions |
| `ebextensions_02_rds.config` | `.ebextensions/02_rds.config` | Move to .ebextensions |
| `ebextensions_03_healthcheck.config` | `.ebextensions/03_healthcheck.config` | Move to .ebextensions |

**Quick way (Linux/macOS):**
```bash
# Rename files
mv templates_index.html templates/index.html
mv ebextensions_01_python.config .ebextensions/01_python.config
mv ebextensions_02_rds.config .ebextensions/02_rds.config
mv ebextensions_03_healthcheck.config .ebextensions/03_healthcheck.config
```

---

## 🧪 Testing Endpoints

### Using curl (Command Line)

```bash
# Test health
curl http://localhost:5000/health

# Calculate: 10 + 5
curl -X POST http://localhost:5000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": "10 + 5"}'

# Calculate: (2 + 3) * 4
curl -X POST http://localhost:5000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": "(2 + 3) * 4"}'

# Get history
curl http://localhost:5000/api/history

# Get statistics
curl http://localhost:5000/api/statistics

# Delete calculation (replace 1 with actual ID)
curl -X DELETE http://localhost:5000/api/history/1
```

### Using Browser

1. **Web Interface**: http://localhost:5000
   - Simple, visual interface
   - Click "Calculate" or press Enter
   - View history on the right

2. **Direct API Testing**: http://localhost:5000/api/statistics
   - Shows JSON statistics
   - Refresh to see updated numbers

---

## 🔍 Common Issues & Solutions

### Issue: Port 5000 Already in Use
```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill process
kill -9 PID  # macOS/Linux
taskkill /PID PID /F  # Windows
```

### Issue: Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose ps

# View logs
docker-compose logs db

# Restart containers
docker-compose down
docker-compose up -d
```

### Issue: EB Deploy Fails
```bash
# Check logs
eb logs --stream

# Check events
eb events

# Abort and retry
eb abort
eb deploy
```

---

## 📊 Next Steps

After successful local testing:

1. **Commit to Git**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Calculator app"
   ```

2. **Push to GitHub** (optional)
   ```bash
   git remote add origin https://github.com/your-repo
   git push -u origin main
   ```

3. **Deploy to AWS**
   - Follow the "30-Minute AWS Deployment" section above

4. **Configure Domain** (optional)
   - Go to Route 53
   - Add CNAME record pointing to EB endpoint

5. **Add SSL/HTTPS** (optional)
   - Request certificate in ACM
   - Attach to load balancer

---

## 🔒 Security Checklist

Before going to production:

- [ ] Change default RDS password
- [ ] Enable SSL/TLS (HTTPS)
- [ ] Set up WAF rules
- [ ] Configure CloudWatch alarms
- [ ] Enable RDS encryption
- [ ] Setup VPC security groups properly
- [ ] Enable CloudTrail logging
- [ ] Configure backup retention

---

## 📞 Help & Troubleshooting

### Check Application Status

```bash
# Local development
docker-compose ps
docker-compose logs -f app

# AWS Elastic Beanstalk
eb status
eb health
eb logs --stream
```

### View Application

```bash
# Local
http://localhost:5000

# AWS
eb open
```

### Debug Database

```bash
# Local (from inside container)
docker-compose exec db psql -U admin -d calculator_db

# Then in psql:
SELECT * FROM calculations LIMIT 5;
```

---

## 💡 Tips

- **Save bandwidth**: Use `docker-compose down` when not testing locally
- **Check costs**: Use AWS Calculator before deploying
- **Monitor usage**: Check CloudWatch dashboards regularly
- **Scale carefully**: Start with t3.micro, upgrade if needed
- **Backup often**: Ensure RDS backups are configured

---

**Ready to go?** Start with **Step 1** above! 🚀

For detailed information, see `DEPLOYMENT_GUIDE.md` or `README.md`
