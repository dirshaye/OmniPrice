import React, { useState } from 'react';
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
  const [products, setProducts] = useState(mockProducts);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    product.sku.toLowerCase().includes(searchQuery.toLowerCase()) ||
    product.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleAddProduct = () => {
    setSelectedProduct(null);
    setDialogOpen(true);
  };

  const handleEditProduct = (product) => {
    setSelectedProduct(product);
    setDialogOpen(true);
  };

  const handleDeleteProduct = (productId) => {
    setProducts(products.filter(p => p.id !== productId));
  };

  const handleSaveProduct = (productData) => {
    if (selectedProduct) {
      // Update existing product
      setProducts(products.map(p => 
        p.id === selectedProduct.id 
          ? { ...p, ...productData }
          : p
      ));
    } else {
      // Add new product
      const newProduct = {
        ...productData,
        id: Math.max(...products.map(p => p.id)) + 1,
        lastUpdated: new Date().toISOString().split('T')[0],
        priceChange: 0,
        competitors: 0,
      };
      setProducts([...products, newProduct]);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'warning';
      case 'discontinued': return 'error';
      default: return 'default';
    }
  };

  const formatPriceChange = (change) => {
    const isPositive = change > 0;
    return (
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        {isPositive ? (
          <TrendingUp sx={{ color: 'success.main', mr: 0.5, fontSize: 16 }} />
        ) : (
          <TrendingDown sx={{ color: 'error.main', mr: 0.5, fontSize: 16 }} />
        )}
        <Typography
          variant="body2"
          sx={{ color: isPositive ? 'success.main' : 'error.main' }}
        >
          {Math.abs(change).toFixed(1)}%
        </Typography>
      </Box>
    );
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Products
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleAddProduct}
        >
          Add Product
        </Button>
      </Box>

      <Paper sx={{ mb: 3, p: 2 }}>
        <TextField
          fullWidth
          placeholder="Search products by name, SKU, or category..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
        />
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Product</TableCell>
              <TableCell>SKU</TableCell>
              <TableCell>Category</TableCell>
              <TableCell align="right">Current Price</TableCell>
              <TableCell align="right">Original Price</TableCell>
              <TableCell align="center">Price Change</TableCell>
              <TableCell align="center">Status</TableCell>
              <TableCell align="center">Competitors</TableCell>
              <TableCell>Last Updated</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredProducts
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((product) => (
                <TableRow key={product.id} hover>
                  <TableCell>
                    <Typography variant="subtitle2">
                      {product.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="textSecondary">
                      {product.sku}
                    </Typography>
                  </TableCell>
                  <TableCell>{product.category}</TableCell>
                  <TableCell align="right">
                    <Typography variant="subtitle2">
                      ${product.currentPrice}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="textSecondary">
                      ${product.originalPrice}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    {formatPriceChange(product.priceChange)}
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={product.status}
                      color={getStatusColor(product.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Typography variant="body2">
                      {product.competitors}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="textSecondary">
                      {product.lastUpdated}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      onClick={() => handleEditProduct(product)}
                      color="primary"
                    >
                      <Edit fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteProduct(product.id)}
                      color="error"
                    >
                      <Delete fontSize="small" />
                    </IconButton>
                    <IconButton size="small" color="info">
                      <Visibility fontSize="small" />
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

      <ProductDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        product={selectedProduct}
        onSave={handleSaveProduct}
      />

      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={handleAddProduct}
      >
        <Add />
      </Fab>
    </Box>
  );
}

export default Products;
