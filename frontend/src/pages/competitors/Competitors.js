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
import { Add, Delete, Edit, Refresh } from '@mui/icons-material';
import { competitorAPI, scraperAPI } from '../../services/api';

const emptyForm = {
  product_id: '',
  competitor_name: '',
  product_url: '',
  is_active: true,
};

function CompetitorDialog({ open, mode, initialValue, onClose, onSubmit }) {
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    if (!initialValue) {
      setForm(emptyForm);
      return;
    }

    setForm({
      product_id: initialValue.product_id || '',
      competitor_name: initialValue.competitor_name || '',
      product_url: initialValue.product_url || '',
      is_active: initialValue.is_active ?? true,
    });
  }, [initialValue]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit({
      product_id: form.product_id,
      competitor_name: form.competitor_name,
      product_url: form.product_url,
      is_active: form.is_active === true || form.is_active === 'true',
    });
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <form onSubmit={handleSubmit}>
        <DialogTitle>{mode === 'edit' ? 'Edit Competitor' : 'Add Competitor'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12}>
              <TextField fullWidth required label="Product ID" name="product_id" value={form.product_id} onChange={handleChange} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth required label="Competitor Name" name="competitor_name" value={form.competitor_name} onChange={handleChange} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth required label="Product URL" name="product_url" value={form.product_url} onChange={handleChange} />
            </Grid>
            <Grid item xs={12}>
              <TextField select fullWidth label="Status" name="is_active" value={String(form.is_active)} onChange={handleChange}>
                <MenuItem value="true">Active</MenuItem>
                <MenuItem value="false">Inactive</MenuItem>
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

function Competitors() {
  const [competitors, setCompetitors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCompetitor, setEditingCompetitor] = useState(null);

  const loadCompetitors = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await competitorAPI.getAll();
      setCompetitors(response.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load competitors');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCompetitors();
  }, []);

  const onCreate = () => {
    setEditingCompetitor(null);
    setDialogOpen(true);
  };

  const onEdit = (competitor) => {
    setEditingCompetitor(competitor);
    setDialogOpen(true);
  };

  const onDelete = async (competitorId) => {
    if (!window.confirm('Delete this competitor?')) return;
    try {
      await competitorAPI.delete(competitorId);
      await loadCompetitors();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete competitor');
    }
  };

  const onSubmit = async (payload) => {
    try {
      if (editingCompetitor) {
        await competitorAPI.update(editingCompetitor.id, payload);
      } else {
        await competitorAPI.create(payload, { enqueue_scrape: true });
      }
      setDialogOpen(false);
      await loadCompetitors();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save competitor');
    }
  };

  const onRefresh = async (competitor) => {
    try {
      await scraperAPI.fetch({
        url: competitor.product_url,
        competitor_id: competitor.id,
        product_id: competitor.product_id,
        allow_playwright_fallback: true,
      });
      await loadCompetitors();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to scrape competitor URL');
    }
  };

  const summary = useMemo(
    () => ({
      total: competitors.length,
      active: competitors.filter((item) => item.is_active).length,
      withPrice: competitors.filter((item) => typeof item.last_price === 'number').length,
    }),
    [competitors]
  );

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h4">Competitors</Typography>
          <Chip label={`${summary.total} total`} color="info" variant="outlined" />
          <Chip label={`${summary.active} active`} color="success" variant="outlined" />
          <Chip label={`${summary.withPrice} priced`} color="warning" variant="outlined" />
        </Box>
        <Button variant="contained" startIcon={<Add />} onClick={onCreate}>Add Competitor</Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Competitor</TableCell>
                <TableCell>Product ID</TableCell>
                <TableCell>URL</TableCell>
                <TableCell>Last Price</TableCell>
                <TableCell>Last Checked</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {!loading && competitors.map((item) => (
                <TableRow key={item.id} hover>
                  <TableCell>{item.competitor_name}</TableCell>
                  <TableCell sx={{ fontFamily: 'monospace' }}>{item.product_id}</TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ maxWidth: 280 }} noWrap title={item.product_url}>
                      {item.product_url}
                    </Typography>
                  </TableCell>
                  <TableCell>{item.last_price != null ? `${item.last_price} ${item.last_currency || ''}` : '-'}</TableCell>
                  <TableCell>{item.last_checked_at ? new Date(item.last_checked_at).toLocaleString() : '-'}</TableCell>
                  <TableCell>
                    <Chip label={item.is_active ? 'Active' : 'Inactive'} color={item.is_active ? 'success' : 'default'} size="small" />
                  </TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => onRefresh(item)} title="Refresh now"><Refresh fontSize="small" /></IconButton>
                    <IconButton size="small" onClick={() => onEdit(item)}><Edit fontSize="small" /></IconButton>
                    <IconButton size="small" color="error" onClick={() => onDelete(item.id)}><Delete fontSize="small" /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        {!loading && competitors.length === 0 && (
          <Box sx={{ p: 3 }}>
            <Typography color="text.secondary">No competitors yet.</Typography>
          </Box>
        )}
        {loading && (
          <Box sx={{ p: 3 }}>
            <Typography>Loading competitors...</Typography>
          </Box>
        )}
      </Paper>

      <CompetitorDialog
        open={dialogOpen}
        mode={editingCompetitor ? 'edit' : 'create'}
        initialValue={editingCompetitor}
        onClose={() => setDialogOpen(false)}
        onSubmit={onSubmit}
      />
    </Box>
  );
}

export default Competitors;
