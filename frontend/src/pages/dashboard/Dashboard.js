import React, { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  List,
  ListItem,
  ListItemText,
  Paper,
  Typography,
} from '@mui/material';
import { AttachMoney, Inventory, PriceChange, TrendingUp } from '@mui/icons-material';
import { Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { analyticsAPI } from '../../services/api';

const COLORS = ['#1976d2', '#26a69a', '#ff7043', '#ab47bc', '#ffa726'];

function MetricCard({ title, value, icon }) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="overline" color="text.secondary">{title}</Typography>
            <Typography variant="h5">{value}</Typography>
          </Box>
          <Box sx={{ color: 'primary.main' }}>{icon}</Box>
        </Box>
      </CardContent>
    </Card>
  );
}

function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dashboard, setDashboard] = useState(null);
  const [trends, setTrends] = useState([]);
  const [distribution, setDistribution] = useState([]);
  const [activity, setActivity] = useState([]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const [dashboardRes, trendsRes, distributionRes, activityRes] = await Promise.all([
          analyticsAPI.getDashboard(),
          analyticsAPI.getPriceTrends(),
          analyticsAPI.getCompetitorDistribution(),
          analyticsAPI.getRecentActivity(),
        ]);

        setDashboard(dashboardRes.data);
        setTrends(trendsRes.data.price_data || []);
        setDistribution(distributionRes.data.competitor_data || []);
        setActivity(activityRes.data.activities || []);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load dashboard data from backend.');
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const summaryItems = useMemo(() => {
    if (!dashboard) return [];
    return [
      { title: 'Total Products', value: dashboard.total_products || 0, icon: <Inventory sx={{ fontSize: 36 }} /> },
      { title: 'Total Revenue', value: `$${(dashboard.total_revenue || 0).toLocaleString()}`, icon: <AttachMoney sx={{ fontSize: 36 }} /> },
      { title: 'Active Rules', value: dashboard.active_rules || 0, icon: <PriceChange sx={{ fontSize: 36 }} /> },
      { title: 'Tracked Competitors', value: dashboard.competitors_tracked || 0, icon: <TrendingUp sx={{ fontSize: 36 }} /> },
    ];
  }, [dashboard]);

  if (loading) {
    return <Typography>Loading dashboard...</Typography>;
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Typography variant="h4">Dashboard</Typography>
        <Chip label="Backend Connected" color="success" variant="outlined" />
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        {summaryItems.map((item) => (
          <Grid item xs={12} sm={6} md={3} key={item.title}>
            <MetricCard title={item.title} value={item.value} icon={item.icon} />
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Price Trends (7 days)</Typography>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={trends}>
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="revenue" stroke="#1976d2" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Competitor Distribution</Typography>
            {distribution.length === 0 ? (
              <Typography color="text.secondary">No competitor data yet.</Typography>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie data={distribution} dataKey="value" nameKey="name" outerRadius={90} label>
                    {distribution.map((entry, index) => (
                      <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Recent Activity</Typography>
            {activity.length === 0 ? (
              <Typography color="text.secondary">No activity yet.</Typography>
            ) : (
              <List>
                {activity.map((item) => (
                  <ListItem key={`${item.timestamp}-${item.message}`} divider>
                    <ListItemText primary={item.message} secondary={item.timestamp} />
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
