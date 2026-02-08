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
import { Add, Delete, Edit } from '@mui/icons-material';
import { productAPI } from '../../services/api';

const emptyForm = {
  name: '',
  sku: '',
  category: '',
  cost: '',
  current_price: '',
  stock_quantity: '',
  is_active: true,
};

function ProductDialog({ open, mode, initialValue, onClose, onSubmit }) {
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    if (!initialValue) {
      setForm(emptyForm);
      return;
    }
    setForm({
      name: initialValue.name || '',
      sku: initialValue.sku || '',
      category: initialValue.category || '',
      cost: initialValue.cost ?? '',
      current_price: initialValue.current_price ?? '',
      stock_quantity: initialValue.stock_quantity ?? '',
      is_active: initialValue.is_active ?? true,
    });
  }, [initialValue]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const payload = {
      name: form.name,
      sku: form.sku || null,
      category: form.category || null,
      cost: form.cost === '' ? null : Number(form.cost),
      current_price: Number(form.current_price),
      stock_quantity: form.stock_quantity === '' ? null : Number(form.stock_quantity),
      is_active: form.is_active === true || form.is_active === 'true',
    };
    onSubmit(payload);
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <form onSubmit={handleSubmit}>
        <DialogTitle>{mode === 'edit' ? 'Edit Product' : 'Add Product'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12}>
              <TextField fullWidth required label="Name" name="name" value={form.name} onChange={handleChange} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="SKU" name="sku" value={form.sku} onChange={handleChange} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Category" name="category" value={form.category} onChange={handleChange} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField fullWidth label="Cost" name="cost" type="number" value={form.cost} onChange={handleChange} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField fullWidth required label="Current Price" name="current_price" type="number" value={form.current_price} onChange={handleChange} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField fullWidth label="Stock Quantity" name="stock_quantity" type="number" value={form.stock_quantity} onChange={handleChange} />
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

function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);

  const loadProducts = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await productAPI.getAll();
      setProducts(response.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const onCreate = () => {
    setEditingProduct(null);
    setDialogOpen(true);
  };

  const onEdit = (product) => {
    setEditingProduct(product);
    setDialogOpen(true);
  };

  const onDelete = async (productId) => {
    if (!window.confirm('Delete this product?')) return;
    try {
      await productAPI.delete(productId);
      await loadProducts();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete product');
    }
  };

  const onSubmit = async (payload) => {
    try {
      if (editingProduct) {
        await productAPI.update(editingProduct.id, payload);
      } else {
        await productAPI.create(payload);
      }
      setDialogOpen(false);
      await loadProducts();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save product');
    }
  };

  const summary = useMemo(
    () => ({
      total: products.length,
      active: products.filter((item) => item.is_active).length,
    }),
    [products]
  );

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h4">Products</Typography>
          <Chip label={`${summary.total} total`} color="info" variant="outlined" />
          <Chip label={`${summary.active} active`} color="success" variant="outlined" />
        </Box>
        <Button variant="contained" startIcon={<Add />} onClick={onCreate}>Add Product</Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>SKU</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Cost</TableCell>
                <TableCell>Current Price</TableCell>
                <TableCell>Stock</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {!loading && products.map((product) => (
                <TableRow key={product.id} hover>
                  <TableCell>{product.name}</TableCell>
                  <TableCell>{product.sku || '-'}</TableCell>
                  <TableCell>{product.category || '-'}</TableCell>
                  <TableCell>{product.cost ?? '-'}</TableCell>
                  <TableCell>{product.current_price}</TableCell>
                  <TableCell>{product.stock_quantity ?? '-'}</TableCell>
                  <TableCell>
                    <Chip label={product.is_active ? 'Active' : 'Inactive'} color={product.is_active ? 'success' : 'default'} size="small" />
                  </TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => onEdit(product)}><Edit fontSize="small" /></IconButton>
                    <IconButton size="small" color="error" onClick={() => onDelete(product.id)}><Delete fontSize="small" /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        {!loading && products.length === 0 && (
          <Box sx={{ p: 3 }}>
            <Typography color="text.secondary">No products yet.</Typography>
          </Box>
        )}
        {loading && (
          <Box sx={{ p: 3 }}>
            <Typography>Loading products...</Typography>
          </Box>
        )}
      </Paper>

      <ProductDialog
        open={dialogOpen}
        mode={editingProduct ? 'edit' : 'create'}
        initialValue={editingProduct}
        onClose={() => setDialogOpen(false)}
        onSubmit={onSubmit}
      />
    </Box>
  );
}

export default Products;
