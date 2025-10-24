# InvGuard - Secure Inventory Management System

A comprehensive, full-stack inventory management system built with React, Flask, and Docker. InvGuard provides secure, scalable inventory tracking with real-time analytics, automated backups, and role-based access control.

## 🚀 Features

### Core Functionality
- **Inventory Management**: Add, edit, delete, and track inventory items
- **Transaction Logging**: Record stock in/out transactions with detailed notes
- **Real-time Analytics**: Comprehensive dashboards with charts and insights
- **Low Stock Alerts**: Automatic notifications for items below reorder levels
- **Role-based Access**: Admin and viewer roles with appropriate permissions

### Security & Reliability
- **JWT Authentication**: Secure token-based authentication
- **Encrypted Backups**: Automated daily backups with GPG encryption
- **Health Monitoring**: Continuous system health checks and alerts
- **Data Integrity**: Backup verification and integrity checks

### User Experience
- **Modern UI**: Clean, responsive interface built with React and Tailwind CSS
- **Real-time Updates**: Live data updates without page refresh
- **Mobile Responsive**: Works seamlessly on desktop and mobile devices
- **Intuitive Navigation**: Easy-to-use interface with clear navigation

## 🏗️ Architecture

```
InvGuard/
├── backend/           # Flask API server
├── frontend/          # React web application
├── cron/             # Backup and monitoring service
└── docker-compose.yml # Container orchestration
```

### Backend (Flask API)
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite with encrypted backups
- **Authentication**: JWT tokens with role-based access
- **API**: RESTful endpoints for all operations
- **CLI**: Command-line interface for system administration

### Frontend (React App)
- **Framework**: React 18 with React Router
- **Styling**: Tailwind CSS for modern UI
- **Charts**: Chart.js for analytics visualization
- **State Management**: React hooks for local state
- **HTTP Client**: Axios for API communication

### Cron Service
- **Backup Automation**: Daily encrypted database backups
- **Health Monitoring**: API and system health checks
- **Maintenance**: Automated cleanup and maintenance tasks
- **Alerting**: Configurable notification system

## 🛠️ Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd InvGuard
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000/api
   - Default credentials: admin/admin

### Manual Setup

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

#### Cron Service Setup
```bash
cd cron
pip install -r requirements.txt
python backup_cron.py
```

## 📖 Usage

### Default Credentials
- **Admin**: username: `admin`, password: `admin`
- **Viewer**: username: `viewer`, password: `viewer123`

### Key Features

#### Inventory Management
- Add new items with SKU, category, quantity, and pricing
- Edit existing items and update quantities
- Delete items (admin only)
- View low stock alerts

#### Transaction Management
- Record stock in/out transactions
- Add notes and track user actions
- Filter transactions by item, type, and date
- View transaction history

#### Analytics Dashboard
- Real-time inventory statistics
- Category-wise summaries
- Stock trend analysis
- Top items by value
- Low stock alerts

#### Backup & Monitoring
- Automated daily backups at 2:00 AM
- Encrypted backup storage
- Health monitoring every hour
- Weekly maintenance tasks
- Configurable retention policies

## 🔧 Configuration

### Environment Variables

#### Backend
```bash
JWT_SECRET_KEY=your-secret-key
DATABASE_PATH=/app/data/inventory.db
FLASK_ENV=development
```

#### Frontend
```bash
REACT_APP_API_URL=http://localhost:5000/api
```

#### Cron Service
```bash
DATABASE_PATH=/app/data/inventory.db
BACKUP_PATH=/app/backups
GPG_PASSPHRASE=your-gpg-passphrase
API_URL=http://backend:5000/api
BACKUP_RETENTION_DAYS=30
```

### Docker Compose
The application uses Docker Compose for orchestration:
- **Backend**: Flask API server on port 5000
- **Frontend**: React app on port 3000
- **Cron**: Backup and monitoring service
- **Volumes**: Persistent data and backup storage

## 🔒 Security

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (admin/viewer)
- Secure password hashing
- Token expiration handling

### Data Protection
- Encrypted database backups
- Secure file permissions (600)
- Environment variable isolation
- Non-root container execution

### Network Security
- CORS configuration
- API endpoint protection
- Health check authentication
- Secure inter-service communication

## 📊 Monitoring & Maintenance

### Health Checks
- API response time monitoring
- Database connectivity checks
- Disk space monitoring
- Backup integrity verification

### Automated Tasks
- **Daily**: Database backup at 2:00 AM
- **Hourly**: Health check monitoring
- **Weekly**: Maintenance and cleanup
- **Monthly**: Full system check

### Logging
- Structured logging with timestamps
- Error tracking and alerting
- Performance monitoring
- Audit trail for transactions

## 🚀 Deployment

### Production Deployment
1. Update environment variables for production
2. Change default passwords and secrets
3. Configure proper SSL certificates
4. Set up external database if needed
5. Configure backup storage location
6. Set up monitoring and alerting

### Scaling
- Horizontal scaling with load balancers
- Database replication for high availability
- Container orchestration with Kubernetes
- CDN for static assets

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Integration Testing
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📝 API Documentation

### Authentication Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Item Management
- `GET /api/items` - List all items
- `POST /api/items` - Create new item
- `PUT /api/items/{id}` - Update item
- `DELETE /api/items/{id}` - Delete item

### Transaction Management
- `GET /api/transactions` - List transactions
- `POST /api/transactions` - Create transaction
- `DELETE /api/transactions/{id}` - Delete transaction

### Analytics
- `GET /api/analytics/dashboard` - Dashboard statistics
- `GET /api/analytics/low-stock` - Low stock items
- `GET /api/analytics/category-summary` - Category summary
- `GET /api/analytics/stock-trends` - Stock trends

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🚨 Troubleshooting

### **Docker Build Issues**

**Problem**: `failed to calculate checksum` error when building cron service
**Solution**: The Docker build context has been fixed. Make sure you're using the updated files.

**Problem**: `COPY ../backend` error
**Solution**: The cron service now uses standalone backup utilities. No backend modules needed.

### **Common Issues**

**1. Containers won't start:**
```bash
# Check Docker is running
docker --version
docker-compose --version

# Check port availability
netstat -tulpn | grep :3000
netstat -tulpn | grep :5000
```

**2. Database connection issues:**
```bash
# Check database file permissions
docker-compose exec backend ls -la /app/data/

# Restart database initialization
docker-compose exec backend python -c "from utils.db import init_db; init_db()"
```

**3. Frontend not loading:**
```bash
# Check if frontend container is running
docker-compose ps frontend

# Check frontend logs
docker-compose logs frontend
```

**4. Backup issues:**
```bash
# Check cron service logs
docker-compose logs cron

# Test backup manually
docker-compose exec cron python backup_cron.py backup
```

**5. Permission issues:**
```bash
# Fix file permissions
chmod +x setup.sh
chmod +x cron/start.sh

# Rebuild containers
docker-compose down
docker-compose up --build -d
```

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the troubleshooting guide

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Complete inventory management system
- Automated backup and monitoring
- Role-based access control
- Real-time analytics dashboard
- Docker containerization

---

**InvGuard** - Secure, Scalable, Simple Inventory Management
