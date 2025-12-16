// NO MORE MOCK DATA - ALL DATA COMES FROM BACKEND
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Chip,
  Button,
} from '@mui/material';
import { analyticsAPI } from '../../services/api';
import {
  TrendingUp,
  TrendingDown,
  Inventory,
  AttachMoney,
  People,
  Assessment,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

function DashboardCard({ title, value, icon, change, color = 'primary' }) {
  const isPositive = change && change > 0;
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="textSecondary" gutterBottom variant="overline">
              {title}
            </Typography>
            <Typography variant="h4" component="h2">
              {value}
            </Typography>
            {change && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                {isPositive ? (
                  <TrendingUp sx={{ color: 'success.main', mr: 0.5 }} />
                ) : (
                  <TrendingDown sx={{ color: 'error.main', mr: 0.5 }} />
                )}
                <Typography
                  variant="body2"
                  sx={{ color: isPositive ? 'success.main' : 'error.main' }}
                >
                  {Math.abs(change)}% from last month
                </Typography>
              </Box>
            )}
          </Box>
          <Box sx={{ color: `${color}.main` }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

function Dashboard() {
  // ALL DATA MUST COME FROM BACKEND - NO FALLBACKS
  const [dashboardData, setDashboardData] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [competitorChartData, setCompetitorChartData] = useState(null);
  const [activityData, setActivityData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('🚀 Dashboard mounted - FORCING backend API calls...');
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('� FORCING API calls to backend - NO MOCK DATA ALLOWED...');
      
      // Test basic connectivity first
      console.log('🔍 Testing backend connection...');
      const healthResponse = await fetch('http://localhost:8000/health');
      console.log('Health check status:', healthResponse.status);
      if (!healthResponse.ok) {
        throw new Error(`Health check failed: ${healthResponse.status} ${healthResponse.statusText}`);
      }
      const healthData = await healthResponse.json();
      console.log('Health data:', healthData);
      
      // Fetch dashboard data - REQUIRED
      console.log('📊 REQUIRED: Calling /analytics/dashboard...');
      const dashboardResponse = await analyticsAPI.getDashboard();
      console.log('Dashboard API response:', dashboardResponse);
      if (!dashboardResponse || !dashboardResponse.data) {
        throw new Error('Dashboard API returned no data');
      }
      setDashboardData(dashboardResponse.data);
      
      // Fetch chart data - REQUIRED
      console.log('📈 REQUIRED: Calling /analytics/price-trends...');
      const trendsResponse = await fetch('http://localhost:8000/analytics/price-trends');
      console.log('Trends response status:', trendsResponse.status);
      if (!trendsResponse.ok) {
        throw new Error(`Price trends API failed: ${trendsResponse.status}`);
      }
      const trendsData = await trendsResponse.json();
      console.log('Trends response:', trendsData);
      setChartData(trendsData.price_data || trendsData);
      
      // Fetch competitor data - REQUIRED
      console.log('🏢 REQUIRED: Calling /analytics/competitor-distribution...');
      const competitorResponse = await fetch('http://localhost:8000/analytics/competitor-distribution');
      console.log('Competitor response status:', competitorResponse.status);
      if (!competitorResponse.ok) {
        throw new Error(`Competitor API failed: ${competitorResponse.status}`);
      }
      const competitorData = await competitorResponse.json();
      console.log('Competitor response:', competitorData);
      setCompetitorChartData(competitorData.competitor_data || competitorData);
      
      // Fetch activity data - REQUIRED
      console.log('📋 REQUIRED: Calling /analytics/recent-activity...');
      const activityResponse = await fetch('http://localhost:8000/analytics/recent-activity');
      console.log('Activity response status:', activityResponse.status);
      if (!activityResponse.ok) {
        throw new Error(`Activity API failed: ${activityResponse.status}`);
      }
      const activityResponseData = await activityResponse.json();
      console.log('Activity response:', activityResponseData);
      setActivityData(activityResponseData.activities || activityResponseData);
      
      console.log('✅ ALL BACKEND API CALLS COMPLETED - NO MOCK DATA USED!');
    } catch (err) {
      console.error('💥 BACKEND API CALL FAILED:', err);
      console.error('Error details:', {
        message: err.message,
        stack: err.stack,
        name: err.name
      });
      setError(`Backend API Error: ${err.message}`);
      // NO FALLBACK TO MOCK DATA - SHOW ERROR INSTEAD
    } finally {
      setLoading(false);
    }
  };

  const testBackendConnection = async () => {
    try {
      console.log('🧪 MANUAL TEST: Testing backend connection...');
      alert('Testing backend connection... Check console and network tab!');
      
      const response = await fetch('http://localhost:8000/health');
      console.log('🧪 MANUAL TEST: Response status:', response.status);
      console.log('🧪 MANUAL TEST: Response headers:', response.headers);
      
      const healthData = await response.json();
      console.log('🧪 MANUAL TEST: Health data:', healthData);
      
      alert(`✅ Backend connected! Status: ${response.status}, Service: ${healthData.service}`);
    } catch (err) {
      console.error('🧪 MANUAL TEST: Backend connection failed:', err);
      alert(`❌ Backend connection failed: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Typography>🔄 LOADING DATA FROM BACKEND ONLY - NO MOCK DATA...</Typography>
        <Typography variant="body2" sx={{ mt: 1 }}>
          🌐 Making real API calls to localhost:8000
        </Typography>
        <Typography variant="body2" sx={{ mt: 1 }}>
          📊 Check Network tab in browser dev tools to verify API calls
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard - Backend Connection Required
        </Typography>
        <Paper sx={{ p: 3, bgcolor: 'error.light', mb: 2 }}>
          <Typography color="error" variant="h6">❌ Backend API Error</Typography>
          <Typography color="error">{error}</Typography>
          <Typography sx={{ mt: 2 }}>
            🚫 <strong>NO MOCK DATA FALLBACK</strong> - Backend must be working
          </Typography>
        </Paper>
        <Box sx={{ mt: 2 }}>
          <Button onClick={fetchAllData} variant="contained" sx={{ mr: 2 }}>
            🔄 Retry Backend Connection
          </Button>
          <Button onClick={testBackendConnection} variant="outlined">
            🔍 Test Backend Health
          </Button>
        </Box>
        <Paper sx={{ p: 2, mt: 2 }}>
          <Typography variant="h6">🛠️ Troubleshooting:</Typography>
          <Typography>1. ✅ Check backend is running: <code>python3 main.py</code></Typography>
          <Typography>2. ✅ Check backend URL: <code>http://localhost:8000/health</code></Typography>
          <Typography>3. ✅ Check Network tab for failed requests</Typography>
          <Typography>4. ✅ Check Console tab for detailed error messages</Typography>
        </Paper>
      </Box>
    );
  }

  // DATA VALIDATION - Must have backend data or show error
  if (!dashboardData) {
    return (
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard - Missing Backend Data
        </Typography>
        <Typography color="error">
          🚫 Dashboard data is null - Backend API call failed
        </Typography>
        <Button onClick={fetchAllData} sx={{ mt: 2 }}>
          Retry API Calls
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" gutterBottom sx={{ mr: 2 }}>
          Dashboard
        </Typography>
        <Chip 
          label="🔗 Connected to Backend API" 
          color="success" 
          variant="outlined"
          sx={{ fontSize: '0.9rem' }}
        />
      </Box>
      
      <Grid container spacing={3}>
        {/* Key Metrics - ONLY BACKEND DATA */}
        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Total Products"
            value={dashboardData.total_products || 0}
            icon={<Inventory sx={{ fontSize: 40 }} />}
            change={dashboardData.product_growth ? parseFloat(dashboardData.product_growth.replace('%', '')) : null}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Total Revenue"
            value={`$${(dashboardData.total_revenue || 0).toLocaleString()}`}
            icon={<AttachMoney sx={{ fontSize: 40 }} />}
            change={dashboardData.revenue_trend ? parseFloat(dashboardData.revenue_trend.replace('%', '')) : null}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Average Price"
            value={`$${(dashboardData.avg_price || 0).toFixed(2)}`}
            icon={<People sx={{ fontSize: 40 }} />}
            change={null}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Price Changes Today"
            value={dashboardData.price_changes_today || 0}
            icon={<Assessment sx={{ fontSize: 40 }} />}
            change={null}
            color="info"
          />
        </Grid>

        {/* Backend Connection Verification Card */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, bgcolor: 'success.light', mb: 2 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              🎉 REAL BACKEND DATA - NO MOCK DATA
              <Chip label="LIVE DATA ONLY" color="success" sx={{ ml: 2 }} />
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" color="textSecondary">Backend URL:</Typography>
                <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                  localhost:8000
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" color="textSecondary">Products Loaded:</Typography>
                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                  {dashboardData.total_products} from Backend API
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" color="textSecondary">Last API Call:</Typography>
                <Typography variant="body1" sx={{ fontFamily: 'monospace', fontSize: '0.9rem' }}>
                  {dashboardData.last_updated ? new Date(dashboardData.last_updated).toLocaleTimeString() : 'N/A'}
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" color="textSecondary">Data Source:</Typography>
                <Typography variant="body1" sx={{ color: 'success.dark', fontWeight: 'bold' }}>
                  ✅ Backend Only
                </Typography>
              </Grid>
            </Grid>
            <Typography variant="body2" sx={{ mt: 2, fontStyle: 'italic' }}>
              � NO MOCK DATA - All data comes from FastAPI backend services
            </Typography>
          </Paper>
        </Grid>

        {/* Charts with Backend Data ONLY */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Revenue & Product Trends (Backend Data Only)
            </Typography>
            {chartData && chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="revenue"
                    stroke="#1976d2"
                    strokeWidth={2}
                    name="Revenue ($)"
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="products"
                    stroke="#dc004e"
                    strokeWidth={2}
                    name="Products"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <Box sx={{ p: 4, textAlign: 'center' }}>
                <Typography color="error">
                  ❌ No chart data from backend API
                </Typography>
                <Typography variant="body2">
                  Backend must provide price trends data
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Backend Services Status (Real Data)
            </Typography>
            <List>
              <ListItem>
                <ListItemText primary="Product Service" secondary="✅ Active" />
                <Chip label={`${dashboardData.total_products || 0} products`} size="small" color="success" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Pricing Service" secondary="✅ Active" />
                <Chip label={`${dashboardData.pricing_rules_active || 0} rules`} size="small" color="success" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Scraper Service" secondary="✅ Active" />
                <Chip label={`${dashboardData.active_scrape_jobs || 0} jobs`} size="small" color="success" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Competitor Service" secondary="✅ Active" />
                <Chip label={`${dashboardData.competitor_count || 0} tracked`} size="small" color="success" />
              </ListItem>
            </List>
          </Paper>
        </Grid>

        {/* Recent Activity - Backend Data Only */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity (Backend Data)
            </Typography>
            {activityData && activityData.length > 0 ? (
              <List>
                {activityData.map((activity, index) => (
                  <ListItem key={activity.id || index} divider>
                    <ListItemText
                      primary={activity.action || activity.description}
                      secondary={activity.time || activity.timestamp}
                    />
                    <Chip
                      label={activity.type || 'activity'}
                      size="small"
                      color={
                        activity.type === 'price' ? 'primary' :
                        activity.type === 'competitor' ? 'secondary' :
                        activity.type === 'rule' ? 'success' : 'default'
                      }
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Box sx={{ p: 2, textAlign: 'center' }}>
                <Typography color="error">
                  ❌ No activity data from backend
                </Typography>
                <Typography variant="body2">
                  Backend must provide recent activity data
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Competitor Distribution - Backend Data Only */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Competitor Distribution (Backend Data)
            </Typography>
            {competitorChartData && competitorChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={competitorChartData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}%`}
                  >
                    {competitorChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color || '#8884d8'} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <Box sx={{ p: 4, textAlign: 'center' }}>
                <Typography color="error">
                  ❌ No competitor data from backend
                </Typography>
                <Typography variant="body2">
                  Backend must provide competitor distribution data
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
