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
  Card,
  CardContent,
  CardActions,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider,
  Alert,
  Tabs,
  Tab,
  LinearProgress,
  InputAdornment,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Search,
  Refresh,
  TrendingUp,
  TrendingDown,
  Link as LinkIcon,
  Store,
  Timeline,
  Warning,
} from '@mui/icons-material';

const mockCompetitors = [
  {
    id: 1,
    name: 'Amazon',
    website: 'amazon.com',
    status: 'active',
    lastScrape: '2024-01-16 15:30',
    productsTracked: 45,
    avgPrice: 425.50,
    priceChange: -2.1,
    reliability: 98.5,
    responseTime: 120,
  },
  {
    id: 2,
    name: 'Best Buy',
    website: 'bestbuy.com',
    status: 'active',
    lastScrape: '2024-01-16 15:25',
    productsTracked: 32,
    avgPrice: 445.75,
    priceChange: 1.8,
    reliability: 95.2,
    responseTime: 180,
  },
  {
    id: 3,
    name: 'Walmart',
    website: 'walmart.com',
    status: 'inactive',
    lastScrape: '2024-01-15 14:20',
    productsTracked: 28,
    avgPrice: 398.25,
    priceChange: -5.3,
    reliability: 87.8,
    responseTime: 250,
  },
  {
    id: 4,
    name: 'Target',
    website: 'target.com',
    status: 'active',
    lastScrape: '2024-01-16 15:28',
    productsTracked: 19,
    avgPrice: 412.90,
    priceChange: 0.5,
    reliability: 92.1,
    responseTime: 165,
  },
  {
    id: 5,
    name: 'Newegg',
    website: 'newegg.com',
    status: 'error',
    lastScrape: '2024-01-16 12:15',
    productsTracked: 15,
    avgPrice: 455.30,
    priceChange: 3.2,
    reliability: 78.9,
    responseTime: 320,
  },
];

const mockProductComparisons = [
  {
    id: 1,
    productName: 'iPhone 15 Pro',
    ourPrice: 999.99,
    competitors: [
      { name: 'Amazon', price: 979.99, inStock: true },
      { name: 'Best Buy', price: 999.99, inStock: true },
      { name: 'Walmart', price: 985.00, inStock: false },
      { name: 'Target', price: 999.99, inStock: true },
    ],
    lowestPrice: 979.99,
    marketPosition: 'Above Average',
  },
  {
    id: 2,
    productName: 'Samsung Galaxy S24',
    ourPrice: 899.99,
    competitors: [
      { name: 'Amazon', price: 899.99, inStock: true },
      { name: 'Best Buy', price: 929.99, inStock: true },
      { name: 'Walmart', price: 895.00, inStock: true },
      { name: 'Target', price: 899.99, inStock: false },
    ],
    lowestPrice: 895.00,
    marketPosition: 'Competitive',
  },
];

function CompetitorDialog({ open, onClose, competitor, onSave }) {
  const [formData, setFormData] = useState(
    competitor || {
      name: '',
      website: '',
      status: 'active',
      scrapeUrl: '',
      scrapeInterval: 60,
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
          {competitor ? 'Edit Competitor' : 'Add New Competitor'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Competitor Name"
                value={formData.name}
                onChange={handleChange('name')}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Website"
                value={formData.website}
                onChange={handleChange('website')}
                placeholder="example.com"
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Scrape URL Pattern"
                value={formData.scrapeUrl}
                onChange={handleChange('scrapeUrl')}
                placeholder="https://example.com/product/{product_id}"
                helperText="Use {product_id} as placeholder for product identifiers"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Scrape Interval (minutes)"
                type="number"
                value={formData.scrapeInterval}
                onChange={handleChange('scrapeInterval')}
                inputProps={{ min: 5, max: 1440 }}
              />
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
                  <MenuItem value="error">Error</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained">
            {competitor ? 'Update' : 'Add'} Competitor
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

function CompetitorCard({ competitor, onEdit, onDelete, onRefresh }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getReliabilityColor = (reliability) => {
    if (reliability >= 95) return 'success';
    if (reliability >= 85) return 'warning';
    return 'error';
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
            <Store />
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6">
              {competitor.name}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {competitor.website}
            </Typography>
          </Box>
          <Chip
            label={competitor.status}
            color={getStatusColor(competitor.status)}
            size="small"
          />
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Typography variant="body2" color="textSecondary">
              Products Tracked
            </Typography>
            <Typography variant="h6">
              {competitor.productsTracked}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="textSecondary">
              Avg Price
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="h6">
                ${competitor.avgPrice}
              </Typography>
              {competitor.priceChange !== 0 && (
                <Box sx={{ display: 'flex', alignItems: 'center', ml: 1 }}>
                  {competitor.priceChange > 0 ? (
                    <TrendingUp sx={{ color: 'error.main', fontSize: 16 }} />
                  ) : (
                    <TrendingDown sx={{ color: 'success.main', fontSize: 16 }} />
                  )}
                  <Typography
                    variant="body2"
                    sx={{ color: competitor.priceChange > 0 ? 'error.main' : 'success.main' }}
                  >
                    {Math.abs(competitor.priceChange)}%
                  </Typography>
                </Box>
              )}
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ my: 2 }} />

        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="body2" color="textSecondary">
              Reliability
            </Typography>
            <Typography variant="body2" color={getReliabilityColor(competitor.reliability)}>
              {competitor.reliability}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={competitor.reliability}
            color={getReliabilityColor(competitor.reliability)}
          />
        </Box>

        <Grid container spacing={1}>
          <Grid item xs={6}>
            <Typography variant="body2" color="textSecondary">
              Response Time
            </Typography>
            <Typography variant="body2">
              {competitor.responseTime}ms
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="textSecondary">
              Last Scrape
            </Typography>
            <Typography variant="body2">
              {competitor.lastScrape.split(' ')[1]}
            </Typography>
          </Grid>
        </Grid>
      </CardContent>
      <CardActions>
        <Button size="small" onClick={() => onEdit(competitor)} startIcon={<Edit />}>
          Edit
        </Button>
        <Button size="small" onClick={() => onRefresh(competitor.id)} startIcon={<Refresh />}>
          Refresh
        </Button>
        <Button size="small" onClick={() => onDelete(competitor.id)} startIcon={<Delete />} color="error">
          Delete
        </Button>
      </CardActions>
    </Card>
  );
}

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`competitors-tabpanel-${index}`}
      aria-labelledby={`competitors-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function Competitors() {
  const [competitors, setCompetitors] = useState(mockCompetitors);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedCompetitor, setSelectedCompetitor] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredCompetitors = competitors.filter(competitor =>
    competitor.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    competitor.website.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleAddCompetitor = () => {
    setSelectedCompetitor(null);
    setDialogOpen(true);
  };

  const handleEditCompetitor = (competitor) => {
    setSelectedCompetitor(competitor);
    setDialogOpen(true);
  };

  const handleDeleteCompetitor = (competitorId) => {
    setCompetitors(competitors.filter(c => c.id !== competitorId));
  };

  const handleRefreshCompetitor = (competitorId) => {
    // In a real app, this would trigger a new scrape
    console.log('Refreshing competitor:', competitorId);
  };

  const handleSaveCompetitor = (competitorData) => {
    if (selectedCompetitor) {
      setCompetitors(competitors.map(c =>
        c.id === selectedCompetitor.id
          ? { ...c, ...competitorData }
          : c
      ));
    } else {
      const newCompetitor = {
        ...competitorData,
        id: Math.max(...competitors.map(c => c.id)) + 1,
        productsTracked: 0,
        avgPrice: 0,
        priceChange: 0,
        reliability: 100,
        responseTime: 0,
        lastScrape: 'Never',
      };
      setCompetitors([...competitors, newCompetitor]);
    }
  };

  const activeCompetitors = competitors.filter(c => c.status === 'active');
  const errorCompetitors = competitors.filter(c => c.status === 'error');

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Competitors
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleAddCompetitor}
        >
          Add Competitor
        </Button>
      </Box>

      {errorCompetitors.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="body2">
            {errorCompetitors.length} competitor{errorCompetitors.length > 1 ? 's have' : ' has'} scraping errors.
            Check your configurations and network connectivity.
          </Typography>
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Overview" />
          <Tab label="Price Comparison" />
          <Tab label="Performance" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Paper sx={{ mb: 3, p: 2 }}>
          <TextField
            fullWidth
            placeholder="Search competitors by name or website..."
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

        <Grid container spacing={3}>
          {filteredCompetitors.map((competitor) => (
            <Grid item xs={12} md={6} lg={4} key={competitor.id}>
              <CompetitorCard
                competitor={competitor}
                onEdit={handleEditCompetitor}
                onDelete={handleDeleteCompetitor}
                onRefresh={handleRefreshCompetitor}
              />
            </Grid>
          ))}
          {filteredCompetitors.length === 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="h6" color="textSecondary">
                  No competitors found
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  {searchQuery ? 'Try adjusting your search terms' : 'Add your first competitor to start tracking prices'}
                </Typography>
                {!searchQuery && (
                  <Button
                    variant="outlined"
                    startIcon={<Add />}
                    onClick={handleAddCompetitor}
                    sx={{ mt: 2 }}
                  >
                    Add Competitor
                  </Button>
                )}
              </Paper>
            </Grid>
          )}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Product</TableCell>
                <TableCell align="right">Our Price</TableCell>
                <TableCell align="right">Lowest Price</TableCell>
                <TableCell align="center">Market Position</TableCell>
                <TableCell>Competitor Prices</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockProductComparisons.map((product) => (
                <TableRow key={product.id} hover>
                  <TableCell>
                    <Typography variant="subtitle2">
                      {product.productName}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="h6">
                      ${product.ourPrice}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography
                      variant="subtitle2"
                      color={product.ourPrice > product.lowestPrice ? 'error.main' : 'success.main'}
                    >
                      ${product.lowestPrice}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={product.marketPosition}
                      color={
                        product.marketPosition === 'Competitive' ? 'success' :
                        product.marketPosition === 'Above Average' ? 'warning' : 'error'
                      }
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <List dense>
                      {product.competitors.map((comp, index) => (
                        <ListItem key={index} sx={{ py: 0.5 }}>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                <Typography variant="body2">
                                  {comp.name}
                                </Typography>
                                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                  ${comp.price}
                                </Typography>
                              </Box>
                            }
                            secondary={
                              <Chip
                                label={comp.inStock ? 'In Stock' : 'Out of Stock'}
                                color={comp.inStock ? 'success' : 'error'}
                                size="small"
                                variant="outlined"
                              />
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Scraping Performance
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                Monitor the reliability and performance of competitor data collection
              </Typography>
              <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'grey.100' }}>
                <Typography variant="body2" color="textSecondary">
                  Performance metrics chart will be displayed here
                </Typography>
              </Box>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Quick Stats
              </Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary="Active Competitors"
                    secondary={
                      <Typography color="success.main">
                        {activeCompetitors.length} tracking
                      </Typography>
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Products Tracked"
                    secondary={`${competitors.reduce((sum, c) => sum + c.productsTracked, 0)} total`}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Avg Response Time"
                    secondary={`${Math.round(competitors.reduce((sum, c) => sum + c.responseTime, 0) / competitors.length)}ms`}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Overall Reliability"
                    secondary={
                      <Typography color="success.main">
                        {Math.round(competitors.reduce((sum, c) => sum + c.reliability, 0) / competitors.length)}%
                      </Typography>
                    }
                  />
                </ListItem>
              </List>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      <CompetitorDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        competitor={selectedCompetitor}
        onSave={handleSaveCompetitor}
      />
    </Box>
  );
}

export default Competitors;
