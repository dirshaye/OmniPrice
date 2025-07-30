import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  Chip,
  Button,
  ButtonGroup,
} from '@mui/material';
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
  AreaChart,
  Area,
  ScatterChart,
  Scatter,
  ComposedChart,
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
  Assessment,
  Timeline,
  PieChart as PieChartIcon,
} from '@mui/icons-material';

// Mock data for analytics
const revenueData = [
  { date: '2024-01-01', revenue: 45000, margin: 18.5, orders: 120, avgOrderValue: 375 },
  { date: '2024-01-02', revenue: 52000, margin: 19.2, orders: 135, avgOrderValue: 385 },
  { date: '2024-01-03', revenue: 48000, margin: 17.8, orders: 128, avgOrderValue: 375 },
  { date: '2024-01-04', revenue: 61000, margin: 20.1, orders: 145, avgOrderValue: 420 },
  { date: '2024-01-05', revenue: 55000, margin: 18.9, orders: 140, avgOrderValue: 393 },
  { date: '2024-01-06', revenue: 67000, margin: 21.3, orders: 160, avgOrderValue: 419 },
  { date: '2024-01-07', revenue: 72000, margin: 22.1, orders: 175, avgOrderValue: 411 },
  { date: '2024-01-08', revenue: 69000, margin: 20.8, orders: 168, avgOrderValue: 411 },
  { date: '2024-01-09', revenue: 74000, margin: 21.9, orders: 180, avgOrderValue: 411 },
  { date: '2024-01-10', revenue: 78000, margin: 23.2, orders: 190, avgOrderValue: 411 },
];

const categoryPerformance = [
  { category: 'Electronics', revenue: 125000, margin: 22.5, growth: 15.2, products: 45 },
  { category: 'Computers', revenue: 98000, margin: 18.9, growth: 8.7, products: 32 },
  { category: 'Audio', revenue: 67000, margin: 25.1, growth: 12.3, products: 28 },
  { category: 'Gaming', revenue: 54000, margin: 20.8, growth: 22.1, products: 19 },
  { category: 'Accessories', revenue: 32000, margin: 35.2, growth: 5.8, products: 26 },
];

const priceOptimizationData = [
  { product: 'iPhone 15 Pro', ourPrice: 999, competitorAvg: 979, optimalPrice: 989, impact: 8.5 },
  { product: 'Samsung Galaxy S24', ourPrice: 899, competitorAvg: 915, optimalPrice: 909, impact: 3.2 },
  { product: 'MacBook Air M3', ourPrice: 1199, competitorAvg: 1225, optimalPrice: 1215, impact: 2.8 },
  { product: 'Sony WH-1000XM5', ourPrice: 349, competitorAvg: 365, optimalPrice: 359, impact: 5.1 },
  { product: 'Dell XPS 13', ourPrice: 1299, competitorAvg: 1280, optimalPrice: 1285, impact: -1.2 },
];

const marketShareData = [
  { name: 'Our Store', value: 28, color: '#1976d2' },
  { name: 'Amazon', value: 35, color: '#FF8042' },
  { name: 'Best Buy', value: 18, color: '#00C49F' },
  { name: 'Walmart', value: 12, color: '#FFBB28' },
  { name: 'Others', value: 7, color: '#8884d8' },
];

const hourlyTraffic = [
  { hour: '00', traffic: 120, conversions: 8 },
  { hour: '01', traffic: 80, conversions: 5 },
  { hour: '02', traffic: 60, conversions: 3 },
  { hour: '03', traffic: 45, conversions: 2 },
  { hour: '04', traffic: 35, conversions: 1 },
  { hour: '05', traffic: 50, conversions: 3 },
  { hour: '06', traffic: 90, conversions: 6 },
  { hour: '07', traffic: 150, conversions: 12 },
  { hour: '08', traffic: 220, conversions: 18 },
  { hour: '09', traffic: 280, conversions: 25 },
  { hour: '10', traffic: 320, conversions: 30 },
  { hour: '11', traffic: 350, conversions: 35 },
  { hour: '12', traffic: 380, conversions: 38 },
  { hour: '13', traffic: 360, conversions: 36 },
  { hour: '14', traffic: 340, conversions: 34 },
  { hour: '15', traffic: 310, conversions: 31 },
  { hour: '16', traffic: 290, conversions: 29 },
  { hour: '17', traffic: 280, conversions: 28 },
  { hour: '18', traffic: 250, conversions: 25 },
  { hour: '19', traffic: 220, conversions: 22 },
  { hour: '20', traffic: 200, conversions: 20 },
  { hour: '21', traffic: 180, conversions: 18 },
  { hour: '22', traffic: 160, conversions: 16 },
  { hour: '23', traffic: 140, conversions: 14 },
];

function MetricCard({ title, value, change, icon, color = 'primary' }) {
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
                  {Math.abs(change)}% vs last period
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

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analytics-tabpanel-${index}`}
      aria-labelledby={`analytics-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function Analytics() {
  const [tabValue, setTabValue] = useState(0);
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('revenue');

  const formatCurrency = (value) => `$${value.toLocaleString()}`;
  const formatPercentage = (value) => `${value}%`;

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Analytics
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              label="Time Range"
            >
              <MenuItem value="1d">Last 24 hours</MenuItem>
              <MenuItem value="7d">Last 7 days</MenuItem>
              <MenuItem value="30d">Last 30 days</MenuItem>
              <MenuItem value="90d">Last 90 days</MenuItem>
            </Select>
          </FormControl>
          <Button variant="outlined">
            Export Report
          </Button>
        </Box>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Revenue"
            value="$78,000"
            change={15.2}
            icon={<AttachMoney sx={{ fontSize: 40 }} />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Profit Margin"
            value="23.2%"
            change={2.8}
            icon={<Timeline sx={{ fontSize: 40 }} />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Orders"
            value="190"
            change={8.5}
            icon={<Assessment sx={{ fontSize: 40 }} />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Avg Order Value"
            value="$411"
            change={-1.2}
            icon={<PieChartIcon sx={{ fontSize: 40 }} />}
            color="warning"
          />
        </Grid>
      </Grid>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Revenue Analysis" />
          <Tab label="Category Performance" />
          <Tab label="Price Optimization" />
          <Tab label="Market Analysis" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">Revenue & Margin Trends</Typography>
                <ButtonGroup size="small">
                  <Button
                    variant={selectedMetric === 'revenue' ? 'contained' : 'outlined'}
                    onClick={() => setSelectedMetric('revenue')}
                  >
                    Revenue
                  </Button>
                  <Button
                    variant={selectedMetric === 'margin' ? 'contained' : 'outlined'}
                    onClick={() => setSelectedMetric('margin')}
                  >
                    Margin
                  </Button>
                  <Button
                    variant={selectedMetric === 'orders' ? 'contained' : 'outlined'}
                    onClick={() => setSelectedMetric('orders')}
                  >
                    Orders
                  </Button>
                </ButtonGroup>
              </Box>
              <ResponsiveContainer width="100%" height={400}>
                <ComposedChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip formatter={(value, name) => [
                    name === 'revenue' ? formatCurrency(value) :
                    name === 'margin' ? formatPercentage(value) : value,
                    name
                  ]} />
                  <Area
                    yAxisId="left"
                    type="monotone"
                    dataKey="revenue"
                    fill="#1976d2"
                    fillOpacity={0.1}
                    stroke="#1976d2"
                    strokeWidth={2}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="margin"
                    stroke="#dc004e"
                    strokeWidth={2}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Hourly Traffic & Conversions
              </Typography>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={hourlyTraffic.slice(-12)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="traffic" stroke="#1976d2" strokeWidth={2} />
                  <Line type="monotone" dataKey="conversions" stroke="#dc004e" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Key Performance Indicators
              </Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary="Conversion Rate"
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <TrendingUp sx={{ color: 'success.main', mr: 0.5, fontSize: 16 }} />
                        <Typography color="success.main">12.8% (+0.5%)</Typography>
                      </Box>
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Return Rate"
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <TrendingDown sx={{ color: 'success.main', mr: 0.5, fontSize: 16 }} />
                        <Typography color="success.main">2.1% (-0.3%)</Typography>
                      </Box>
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Customer Satisfaction"
                    secondary="4.7/5.0 ⭐"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Inventory Turnover"
                    secondary="8.5x annually"
                  />
                </ListItem>
              </List>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Category Performance Comparison
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={categoryPerformance}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip formatter={(value, name) => [
                    name === 'revenue' ? formatCurrency(value) :
                    name === 'margin' || name === 'growth' ? formatPercentage(value) : value,
                    name
                  ]} />
                  <Bar yAxisId="left" dataKey="revenue" fill="#1976d2" />
                  <Bar yAxisId="right" dataKey="margin" fill="#dc004e" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Category Insights
              </Typography>
              <List>
                {categoryPerformance.map((category) => (
                  <ListItem key={category.category}>
                    <ListItemText
                      primary={category.category}
                      secondary={
                        <Box>
                          <Typography variant="body2">
                            Revenue: {formatCurrency(category.revenue)}
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                            <Chip
                              label={`${category.growth > 0 ? '+' : ''}${category.growth}% growth`}
                              color={category.growth > 0 ? 'success' : 'error'}
                              size="small"
                            />
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Price Optimization Analysis
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <ScatterChart data={priceOptimizationData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="competitorAvg" name="Competitor Average" />
                  <YAxis dataKey="ourPrice" name="Our Price" />
                  <Tooltip
                    cursor={{ strokeDasharray: '3 3' }}
                    formatter={(value, name) => [formatCurrency(value), name]}
                    labelFormatter={(label) => `Competitor Avg: ${formatCurrency(label)}`}
                  />
                  <Scatter dataKey="ourPrice" fill="#1976d2" />
                </ScatterChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Optimization Opportunities
              </Typography>
              <List>
                {priceOptimizationData
                  .sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact))
                  .slice(0, 5)
                  .map((product, index) => (
                    <ListItem key={index}>
                      <ListItemText
                        primary={product.product}
                        secondary={
                          <Box>
                            <Typography variant="body2">
                              Current: {formatCurrency(product.ourPrice)}
                            </Typography>
                            <Typography variant="body2">
                              Optimal: {formatCurrency(product.optimalPrice)}
                            </Typography>
                            <Chip
                              label={`${product.impact > 0 ? '+' : ''}${product.impact}% impact`}
                              color={product.impact > 0 ? 'success' : 'error'}
                              size="small"
                              sx={{ mt: 0.5 }}
                            />
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
              </List>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Market Share Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={marketShareData}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}%`}
                  >
                    {marketShareData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Competitive Position
              </Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary="Market Position"
                    secondary={
                      <Chip label="2nd Place" color="success" />
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Price Competitiveness"
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography color="warning.main">Moderate (85%)</Typography>
                      </Box>
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Market Share Growth"
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <TrendingUp sx={{ color: 'success.main', mr: 0.5, fontSize: 16 }} />
                        <Typography color="success.main">+2.3% YoY</Typography>
                      </Box>
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Competitive Advantage"
                    secondary="Premium product quality, fast shipping"
                  />
                </ListItem>
              </List>
            </Paper>
          </Grid>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Market Trends & Insights
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        🔥 Trending Products
                      </Typography>
                      <Typography variant="body2">
                        Gaming accessories showing 25% increase in demand
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        📉 Price Drops
                      </Typography>
                      <Typography variant="body2">
                        Competitors reducing prices on electronics by avg 8%
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        🎯 Opportunities
                      </Typography>
                      <Typography variant="body2">
                        Audio category has 15% higher margins than competitors
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>
    </Box>
  );
}

export default Analytics;
