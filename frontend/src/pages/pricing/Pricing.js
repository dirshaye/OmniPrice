import React, { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  IconButton,
  MenuItem,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { Add, Delete, Edit, PlayArrow } from '@mui/icons-material';
import { pricingAPI, productAPI } from '../../services/api';

const emptyRule = {
  name: '',
  description: '',
  type: 'competitive',
  category: '',
  adjustment: 0,
  status: 'active',
};

function RuleDialog({ open, mode, initialValue, onClose, onSubmit }) {
  const [form, setForm] = useState(emptyRule);

  useEffect(() => {
    if (!initialValue) {
      setForm(emptyRule);
      return;
    }
    setForm({
      name: initialValue.name || '',
      description: initialValue.description || '',
      type: initialValue.type || 'competitive',
      category: initialValue.category || '',
      adjustment: initialValue.adjustment ?? 0,
      status: initialValue.status || 'active',
    });
  }, [initialValue]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit({
      name: form.name,
      description: form.description || null,
      type: form.type,
      category: form.category || null,
      adjustment: Number(form.adjustment),
      status: form.status,
    });
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <form onSubmit={handleSubmit}>
        <DialogTitle>{mode === 'edit' ? 'Edit Pricing Rule' : 'Create Pricing Rule'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12}>
              <TextField fullWidth required label="Rule Name" name="name" value={form.name} onChange={handleChange} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="Description" name="description" value={form.description} onChange={handleChange} multiline minRows={2} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField select fullWidth label="Type" name="type" value={form.type} onChange={handleChange}>
                <MenuItem value="competitive">Competitive</MenuItem>
                <MenuItem value="fixed">Fixed</MenuItem>
                <MenuItem value="dynamic">Dynamic</MenuItem>
                <MenuItem value="clearance">Clearance</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Category" name="category" value={form.category} onChange={handleChange} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Adjustment (%)" name="adjustment" type="number" value={form.adjustment} onChange={handleChange} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField select fullWidth label="Status" name="status" value={form.status} onChange={handleChange}>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained">{mode === 'edit' ? 'Update' : 'Create'}</Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

function Pricing() {
  const [rules, setRules] = useState([]);
  const [products, setProducts] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingRule, setEditingRule] = useState(null);

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const [rulesResponse, productsResponse] = await Promise.all([
        pricingAPI.getRules(),
        productAPI.getAll(),
      ]);
      setRules(rulesResponse.data || []);
      setProducts(productsResponse.data || []);
      if (!selectedProductId && (productsResponse.data || []).length > 0) {
        setSelectedProductId(productsResponse.data[0].id);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load pricing data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const onCreate = () => {
    setEditingRule(null);
    setDialogOpen(true);
  };

  const onEdit = (rule) => {
    setEditingRule(rule);
    setDialogOpen(true);
  };

  const onDelete = async (ruleId) => {
    if (!window.confirm('Delete this pricing rule?')) return;
    try {
      await pricingAPI.deleteRule(ruleId);
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete pricing rule');
    }
  };

  const onSubmit = async (payload) => {
    try {
      if (editingRule) {
        await pricingAPI.updateRule(editingRule.id, payload);
      } else {
        await pricingAPI.createRule(payload);
      }
      setDialogOpen(false);
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save pricing rule');
    }
  };

  const onRecommend = async () => {
    if (!selectedProductId) return;
    try {
      const response = await pricingAPI.getRecommendation(selectedProductId);
      setRecommendation(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to compute recommendation');
    }
  };

  const activeCount = useMemo(() => rules.filter((rule) => rule.status === 'active').length, [rules]);

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h4">Pricing</Typography>
          <Chip label={`${rules.length} rules`} color="info" variant="outlined" />
          <Chip label={`${activeCount} active`} color="success" variant="outlined" />
        </Box>
        <Button variant="contained" startIcon={<Add />} onClick={onCreate}>Create Rule</Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Rule-Based Recommendation</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={8}>
                <TextField
                  select
                  fullWidth
                  label="Product"
                  value={selectedProductId}
                  onChange={(event) => setSelectedProductId(event.target.value)}
                >
                  {products.map((product) => (
                    <MenuItem key={product.id} value={product.id}>{product.name}</MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} md={4}>
                <Button fullWidth variant="outlined" startIcon={<PlayArrow />} onClick={onRecommend} sx={{ height: '56px' }}>
                  Recommend
                </Button>
              </Grid>
            </Grid>
            {recommendation && (
              <Box sx={{ mt: 2 }}>
                <Typography>Current price: {recommendation.current_price}</Typography>
                <Typography>Suggested price: {recommendation.suggested_price}</Typography>
                <Typography color="text.secondary">Reason: {recommendation.reason}</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Adjustment</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {!loading && rules.map((rule) => (
                <TableRow key={rule.id} hover>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>{rule.name}</Typography>
                    <Typography variant="caption" color="text.secondary">{rule.description || '-'}</Typography>
                  </TableCell>
                  <TableCell>{rule.type}</TableCell>
                  <TableCell>{rule.category || '-'}</TableCell>
                  <TableCell>{rule.adjustment}%</TableCell>
                  <TableCell>
                    <Chip label={rule.status} color={rule.status === 'active' ? 'success' : 'default'} size="small" />
                  </TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => onEdit(rule)}><Edit fontSize="small" /></IconButton>
                    <IconButton size="small" color="error" onClick={() => onDelete(rule.id)}><Delete fontSize="small" /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        {!loading && rules.length === 0 && (
          <Box sx={{ p: 3 }}>
            <Typography color="text.secondary">No pricing rules yet.</Typography>
          </Box>
        )}
        {loading && (
          <Box sx={{ p: 3 }}>
            <Typography>Loading pricing data...</Typography>
          </Box>
        )}
      </Paper>

      <RuleDialog
        open={dialogOpen}
        mode={editingRule ? 'edit' : 'create'}
        initialValue={editingRule}
        onClose={() => setDialogOpen(false)}
        onSubmit={onSubmit}
      />
    </Box>
  );
}

export default Pricing;
