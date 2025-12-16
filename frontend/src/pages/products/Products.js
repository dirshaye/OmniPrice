import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Fab,
  TablePagination,
  InputAdornment,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Search,
  Visibility,
  TrendingUp,
  TrendingDown,
} from '@mui/icons-material';
import { productAPI } from '../../services/api';

// Mock data
const mockProducts = [
  {
    id: 1,
    name: 'iPhone 15 Pro',
    sku: 'APPL-IP15P-128',
    category: 'Electronics',
    currentPrice: 999.99,
    originalPrice: 1099.99,
    status: 'active',
    lastUpdated: '2024-01-15',
    priceChange: -9.1,
    competitors: 3,
  },
  {
    id: 2,
    name: 'Samsung Galaxy S24',
    sku: 'SAMS-GS24-256',
    category: 'Electronics',
    currentPrice: 899.99,
    originalPrice: 849.99,
    status: 'active',
    lastUpdated: '2024-01-14',
    priceChange: 5.9,
    competitors: 5,
  },
  {
    id: 3,
    name: 'MacBook Air M3',
    sku: 'APPL-MBA-M3-13',
    category: 'Computers',
    currentPrice: 1199.99,
    originalPrice: 1299.99,
    status: 'inactive',
    lastUpdated: '2024-01-10',
    priceChange: -7.7,
    competitors: 2,
  },
  {
    id: 4,
    name: 'Sony WH-1000XM5',
    sku: 'SONY-WH1000XM5',
    category: 'Audio',
    currentPrice: 349.99,
    originalPrice: 399.99,
    status: 'active',
    lastUpdated: '2024-01-16',
    priceChange: -12.5,
    competitors: 4,
  },
  {
    id: 5,
    name: 'Dell XPS 13',
    sku: 'DELL-XPS13-I7',
    category: 'Computers',
    currentPrice: 1299.99,
    originalPrice: 1199.99,
    status: 'active',
    lastUpdated: '2024-01-12',
    priceChange: 8.3,
    competitors: 3,
  },
];

function ProductDialog({ open, onClose, product, onSave }) {
  const [formData, setFormData] = useState(
    product || {
      name: '',
      sku: '',
      category: '',
      currentPrice: '',
      originalPrice: '',
      status: 'active',
    }
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
    onClose();
  };

  const handleChange = (field) => (event) => {
    setFormData({ ...formData, [field]: event.target.value });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>
          {product ? 'Edit Product' : 'Add New Product'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Product Name"
                value={formData.name}
                onChange={handleChange('name')}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="SKU"
                value={formData.sku}
                onChange={handleChange('sku')}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={formData.category}
                  onChange={handleChange('category')}
                  label="Category"
                  required
                >
                  <MenuItem value="Electronics">Electronics</MenuItem>
                  <MenuItem value="Computers">Computers</MenuItem>
                  <MenuItem value="Audio">Audio</MenuItem>
                  <MenuItem value="Gaming">Gaming</MenuItem>
                  <MenuItem value="Accessories">Accessories</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  onChange={handleChange('status')}
                  label="Status"
                >
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="inactive">Inactive</MenuItem>
                  <MenuItem value="discontinued">Discontinued</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Current Price"
                type="number"
                value={formData.currentPrice}
                onChange={handleChange('currentPrice')}
                InputProps={{
                  startAdornment: <InputAdornment position="start">$</InputAdornment>,
                }}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Original Price"
                type="number"
                value={formData.originalPrice}
                onChange={handleChange('originalPrice')}
                InputProps={{
                  startAdornment: <InputAdornment position="start">$</InputAdornment>,
                }}
                required
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained">
            {product ? 'Update' : 'Add'} Product
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    sku: '',
    category: '',
    price: '',
    description: '',
    brand: ''
  });

  // Fetch products from backend
  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await productAPI.getAll();
      // Transform backend data to match frontend expectations
      const transformedProducts = response.products.map(product => ({
        id: product.id,
        name: product.name,
        sku: product.sku || `SKU-${product.id}`,
        category: product.category,
        currentPrice: product.price,
        originalPrice: product.price * 1.1, // Mock original price
        status: 'active',
        lastUpdated: new Date(product.created_at).toISOString().split('T')[0],
        priceChange: Math.random() * 20 - 10, // Mock price change
        competitors: Math.floor(Math.random() * 5) + 1, // Mock competitor count
        description: product.description,
        brand: product.brand
      }));
      setProducts(transformedProducts);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch products:', err);
      setError('Failed to load products from backend');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProduct = async () => {
    try {
      const newProduct = {
        name: formData.name,
        description: formData.description,
        price: parseFloat(formData.price),
        category: formData.category,
        brand: formData.brand
      };
      await productAPI.create(newProduct);
      await fetchProducts(); // Refresh the list
      setOpenDialog(false);
      resetForm();
    } catch (err) {
      console.error('Failed to create product:', err);
      alert('Failed to create product');
    }
  };

  const handleUpdateProduct = async () => {
    try {
      const updatedProduct = {
        name: formData.name,
        description: formData.description,
        price: parseFloat(formData.price),
        category: formData.category,
        brand: formData.brand
      };
      await productAPI.update(editingProduct.id, updatedProduct);
      await fetchProducts(); // Refresh the list
      setOpenDialog(false);
      setEditingProduct(null);
      resetForm();
    } catch (err) {
      console.error('Failed to update product:', err);
      alert('Failed to update product');
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await productAPI.delete(productId);
        await fetchProducts(); // Refresh the list
      } catch (err) {
        console.error('Failed to delete product:', err);
        alert('Failed to delete product');
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      sku: '',
      category: '',
      price: '',
      description: '',
      brand: ''
    });
  };

  const openEditDialog = (product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name,
      sku: product.sku,
      category: product.category,
      price: product.currentPrice.toString(),
      description: product.description || '',
      brand: product.brand || ''
    });
    setOpenDialog(true);
  };

  const openCreateDialog = () => {
    setEditingProduct(null);
    resetForm();
    setOpenDialog(true);
  };

  // Filter products based on search and category
  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.sku.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === '' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Get unique categories for filter
  const categories = [...new Set(products.map(p => p.category))];

  if (loading) {
    return (
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Products
        </Typography>
        <Typography>Loading products from backend...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Products
        </Typography>
        <Typography color="error">{error}</Typography>
        <Button onClick={fetchProducts} sx={{ mt: 2 }}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" gutterBottom sx={{ mr: 2 }}>
          Products
        </Typography>
        <Chip 
          label="🔗 Live from Backend API" 
          color="success" 
          variant="outlined"
          sx={{ fontSize: '0.9rem' }}
        />
        <Chip 
          label={`${products.length} products loaded`} 
          color="info" 
          variant="outlined"
          sx={{ ml: 1, fontSize: '0.9rem' }}
        />
      </Box>
      
      {/* Search and Filter Controls */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            placeholder="Search products..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <FormControl fullWidth>
            <InputLabel>Category</InputLabel>
            <Select
              value={selectedCategory}
              label="Category"
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <MenuItem value="">All Categories</MenuItem>
              {categories.map((category) => (
                <MenuItem key={category} value={category}>
                  {category}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={3}>
          <Button
            fullWidth
            variant="contained"
            startIcon={<Add />}
            onClick={openCreateDialog}
            sx={{ height: '56px' }}
          >
            Add Product
          </Button>
        </Grid>
      </Grid>

      {/* Products Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Product Name</TableCell>
              <TableCell>SKU</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Current Price</TableCell>
              <TableCell>Price Change</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredProducts
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((product) => (
                <TableRow key={product.id}>
                  <TableCell>
                    <Typography variant="subtitle1">{product.name}</Typography>
                    <Typography variant="body2" color="textSecondary">
                      {product.brand}
                    </Typography>
                  </TableCell>
                  <TableCell>{product.sku}</TableCell>
                  <TableCell>
                    <Chip label={product.category} size="small" />
                  </TableCell>
                  <TableCell>${product.currentPrice}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {product.priceChange > 0 ? (
                        <TrendingUp sx={{ color: 'success.main', mr: 0.5 }} />
                      ) : (
                        <TrendingDown sx={{ color: 'error.main', mr: 0.5 }} />
                      )}
                      <Typography
                        variant="body2"
                        sx={{
                          color: product.priceChange > 0 ? 'success.main' : 'error.main',
                        }}
                      >
                        {product.priceChange.toFixed(1)}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={product.status}
                      color={product.status === 'active' ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton onClick={() => openEditDialog(product)} size="small">
                      <Edit />
                    </IconButton>
                    <IconButton 
                      onClick={() => handleDeleteProduct(product.id)} 
                      size="small"
                      color="error"
                    >
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredProducts.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(event, newPage) => setPage(newPage)}
          onRowsPerPageChange={(event) => {
            setRowsPerPage(parseInt(event.target.value, 10));
            setPage(0);
          }}
        />
      </TableContainer>

      {/* Add/Edit Product Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingProduct ? 'Edit Product' : 'Add New Product'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Product Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Brand"
                value={formData.brand}
                onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Category"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Price"
                type="number"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button 
            onClick={editingProduct ? handleUpdateProduct : handleCreateProduct}
            variant="contained"
          >
            {editingProduct ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Products;
