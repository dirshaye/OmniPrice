import React, { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Chip,
  Grid,
  MenuItem,
  Paper,
  TextField,
  Typography,
} from '@mui/material';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { analyticsAPI, productAPI } from '../services/api';

function Analytics() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [performance, setPerformance] = useState(null);
  const [marketTrends, setMarketTrends] = useState([]);
  const [products, setProducts] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [priceHistory, setPriceHistory] = useState([]);

  const loadBaseData = async () => {
    setLoading(true);
    setError('');
    try {
      const [perfRes, marketRes, productsRes] = await Promise.all([
        analyticsAPI.getPerformanceMetrics(),
        analyticsAPI.getMarketTrends(14),
        productAPI.getAll(),
      ]);
      setPerformance(perfRes.data);
      setMarketTrends(marketRes.data.market_trends || []);
      setProducts(productsRes.data || []);
      const firstProduct = (productsRes.data || [])[0];
      if (firstProduct) {
        setSelectedProductId(firstProduct.id);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBaseData();
  }, []);

  useEffect(() => {
    const loadHistory = async () => {
      if (!selectedProductId) {
        setPriceHistory([]);
        return;
      }
      try {
        const response = await analyticsAPI.getPriceHistory(selectedProductId, 30);
        setPriceHistory(response.data.price_history || []);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load price history');
      }
    };

    loadHistory();
  }, [selectedProductId]);

  if (loading) {
    return <Typography>Loading analytics...</Typography>;
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Typography variant="h4">Analytics</Typography>
        <Chip label="Backend Data" color="success" variant="outlined" />
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {performance && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="overline" color="text.secondary">Active Competitors</Typography>
              <Typography variant="h5">{performance.active_competitors}</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="overline" color="text.secondary">Total Competitors</Typography>
              <Typography variant="h5">{performance.total_competitors}</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="overline" color="text.secondary">Price Points</Typography>
              <Typography variant="h5">{performance.total_price_points}</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="overline" color="text.secondary">Rule Activation Rate</Typography>
              <Typography variant="h5">{performance.rule_activation_rate}%</Typography>
            </Paper>
          </Grid>
        </Grid>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Market Trends (14 days)</Typography>
            {marketTrends.length === 0 ? (
              <Typography color="text.secondary">No market trend data yet.</Typography>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={marketTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="competitor_id" hide />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="avg_price" fill="#1976d2" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Product Price History (30 days)</Typography>
            <TextField
              select
              fullWidth
              label="Product"
              value={selectedProductId}
              onChange={(event) => setSelectedProductId(event.target.value)}
              sx={{ mb: 2 }}
            >
              {products.map((product) => (
                <MenuItem key={product.id} value={product.id}>{product.name}</MenuItem>
              ))}
            </TextField>
            {priceHistory.length === 0 ? (
              <Typography color="text.secondary">No price history for selected product.</Typography>
            ) : (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart
                  data={priceHistory.map((entry) => ({
                    ...entry,
                    captured_at: new Date(entry.captured_at).toLocaleDateString(),
                  }))}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="captured_at" hide />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="price" fill="#26a69a" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Analytics;
