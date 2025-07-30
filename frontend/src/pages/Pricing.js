import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Switch,
  FormControlLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tabs,
  Tab,
  Alert,
  InputAdornment,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  PlayArrow,
  Pause,
  Settings,
  TrendingUp,
  TrendingDown,
  Timeline,
} from '@mui/icons-material';

const mockPricingRules = [
  {
    id: 1,
    name: 'Competitive Pricing - Electronics',
    description: 'Automatically adjust prices to stay 5% below competitor average',
    type: 'competitive',
    status: 'active',
    category: 'Electronics',
    adjustment: -5,
    conditions: ['competitor_price_below_threshold', 'stock_available'],
    products: 25,
    lastTriggered: '2024-01-15 14:30',
    impact: { revenue: 12.5, margin: -2.1 }
  },
  {
    id: 2,
    name: 'Dynamic Pricing - High Demand',
    description: 'Increase prices by 10% when demand exceeds supply',
    type: 'dynamic',
    status: 'active',
    category: 'All Categories',
    adjustment: 10,
    conditions: ['high_demand', 'low_stock'],
    products: 50,
    lastTriggered: '2024-01-14 09:15',
    impact: { revenue: 8.3, margin: 15.2 }
  },
  {
    id: 3,
    name: 'Clearance Pricing',
    description: 'Reduce prices by 20% for products with high inventory',
    type: 'clearance',
    status: 'inactive',
    category: 'Audio',
    adjustment: -20,
    conditions: ['high_inventory', 'slow_moving'],
    products: 12,
    lastTriggered: '2024-01-10 16:45',
    impact: { revenue: -5.7, margin: -12.8 }
  },
  {
    id: 4,
    name: 'Premium Product Markup',
    description: 'Maintain premium pricing for flagship products',
    type: 'fixed',
    status: 'active',
    category: 'Computers',
    adjustment: 15,
    conditions: ['premium_brand', 'new_release'],
    products: 8,
    lastTriggered: '2024-01-16 11:20',
    impact: { revenue: 22.1, margin: 18.9 }
  },
];

const mockPriceHistory = [
  { date: '2024-01-10', avgPrice: 450, rules: 3, adjustments: 15 },
  { date: '2024-01-11', avgPrice: 442, rules: 4, adjustments: 22 },
  { date: '2024-01-12', avgPrice: 465, rules: 4, adjustments: 18 },
  { date: '2024-01-13', avgPrice: 458, rules: 3, adjustments: 20 },
  { date: '2024-01-14', avgPrice: 472, rules: 4, adjustments: 25 },
  { date: '2024-01-15', avgPrice: 468, rules: 4, adjustments: 19 },
  { date: '2024-01-16', avgPrice: 475, rules: 4, adjustments: 23 },
];

function PricingRuleDialog({ open, onClose, rule, onSave }) {
  const [formData, setFormData] = useState(
    rule || {
      name: '',
      description: '',
      type: 'competitive',
      category: '',
      adjustment: 0,
      conditions: [],
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
          {rule ? 'Edit Pricing Rule' : 'Create New Pricing Rule'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Rule Name"
                value={formData.name}
                onChange={handleChange('name')}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={handleChange('description')}
                multiline
                rows={2}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Rule Type</InputLabel>
                <Select
                  value={formData.type}
                  onChange={handleChange('type')}
                  label="Rule Type"
                  required
                >
                  <MenuItem value="competitive">Competitive Pricing</MenuItem>
                  <MenuItem value="dynamic">Dynamic Pricing</MenuItem>
                  <MenuItem value="clearance">Clearance Pricing</MenuItem>
                  <MenuItem value="fixed">Fixed Markup</MenuItem>
                  <MenuItem value="bundle">Bundle Pricing</MenuItem>
                </Select>
              </FormControl>
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
                  <MenuItem value="All Categories">All Categories</MenuItem>
                  <MenuItem value="Electronics">Electronics</MenuItem>
                  <MenuItem value="Computers">Computers</MenuItem>
                  <MenuItem value="Audio">Audio</MenuItem>
                  <MenuItem value="Gaming">Gaming</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Price Adjustment"
                type="number"
                value={formData.adjustment}
                onChange={handleChange('adjustment')}
                InputProps={{
                  endAdornment: <InputAdornment position="end">%</InputAdornment>,
                }}
                required
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
                  <MenuItem value="draft">Draft</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained">
            {rule ? 'Update' : 'Create'} Rule
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

function PricingRuleCard({ rule, onEdit, onToggle, onDelete }) {
  const getRuleTypeColor = (type) => {
    switch (type) {
      case 'competitive': return 'primary';
      case 'dynamic': return 'secondary';
      case 'clearance': return 'warning';
      case 'fixed': return 'success';
      default: return 'default';
    }
  };

  const getImpactColor = (value) => value > 0 ? 'success.main' : 'error.main';

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" gutterBottom>
              {rule.name}
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              {rule.description}
            </Typography>
          </Box>
          <FormControlLabel
            control={
              <Switch
                checked={rule.status === 'active'}
                onChange={() => onToggle(rule.id)}
                color="primary"
              />
            }
            label=""
          />
        </Box>

        <Box sx={{ mb: 2 }}>
          <Chip
            label={rule.type}
            color={getRuleTypeColor(rule.type)}
            size="small"
            sx={{ mr: 1 }}
          />
          <Chip
            label={rule.category}
            variant="outlined"
            size="small"
            sx={{ mr: 1 }}
          />
          <Chip
            label={`${rule.adjustment > 0 ? '+' : ''}${rule.adjustment}%`}
            color={rule.adjustment > 0 ? 'success' : 'error'}
            size="small"
          />
        </Box>

        <Divider sx={{ my: 2 }} />

        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Typography variant="body2" color="textSecondary">
              Products Affected
            </Typography>
            <Typography variant="h6">
              {rule.products}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="textSecondary">
              Last Triggered
            </Typography>
            <Typography variant="body2">
              {rule.lastTriggered}
            </Typography>
          </Grid>
        </Grid>

        {rule.impact && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Impact
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUp sx={{ color: getImpactColor(rule.impact.revenue), mr: 0.5, fontSize: 16 }} />
                <Typography variant="body2" sx={{ color: getImpactColor(rule.impact.revenue) }}>
                  Revenue: {rule.impact.revenue > 0 ? '+' : ''}{rule.impact.revenue}%
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {rule.impact.margin > 0 ? (
                  <TrendingUp sx={{ color: 'success.main', mr: 0.5, fontSize: 16 }} />
                ) : (
                  <TrendingDown sx={{ color: 'error.main', mr: 0.5, fontSize: 16 }} />
                )}
                <Typography variant="body2" sx={{ color: getImpactColor(rule.impact.margin) }}>
                  Margin: {rule.impact.margin > 0 ? '+' : ''}{rule.impact.margin}%
                </Typography>
              </Box>
            </Box>
          </Box>
        )}
      </CardContent>
      <CardActions>
        <Button size="small" onClick={() => onEdit(rule)} startIcon={<Edit />}>
          Edit
        </Button>
        <Button size="small" onClick={() => onDelete(rule.id)} startIcon={<Delete />} color="error">
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
      id={`pricing-tabpanel-${index}`}
      aria-labelledby={`pricing-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function Pricing() {
  const [rules, setRules] = useState(mockPricingRules);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedRule, setSelectedRule] = useState(null);
  const [tabValue, setTabValue] = useState(0);

  const handleAddRule = () => {
    setSelectedRule(null);
    setDialogOpen(true);
  };

  const handleEditRule = (rule) => {
    setSelectedRule(rule);
    setDialogOpen(true);
  };

  const handleToggleRule = (ruleId) => {
    setRules(rules.map(rule =>
      rule.id === ruleId
        ? { ...rule, status: rule.status === 'active' ? 'inactive' : 'active' }
        : rule
    ));
  };

  const handleDeleteRule = (ruleId) => {
    setRules(rules.filter(rule => rule.id !== ruleId));
  };

  const handleSaveRule = (ruleData) => {
    if (selectedRule) {
      setRules(rules.map(rule =>
        rule.id === selectedRule.id
          ? { ...rule, ...ruleData }
          : rule
      ));
    } else {
      const newRule = {
        ...ruleData,
        id: Math.max(...rules.map(r => r.id)) + 1,
        products: 0,
        lastTriggered: 'Never',
        impact: { revenue: 0, margin: 0 }
      };
      setRules([...rules, newRule]);
    }
  };

  const activeRules = rules.filter(rule => rule.status === 'active');
  const inactiveRules = rules.filter(rule => rule.status !== 'active');

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Pricing Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleAddRule}
        >
          Create Rule
        </Button>
      </Box>

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          You have {activeRules.length} active pricing rules affecting {rules.reduce((sum, rule) => sum + rule.products, 0)} products.
          Rules are evaluated every 5 minutes.
        </Typography>
      </Alert>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label={`Active Rules (${activeRules.length})`} />
          <Tab label={`Inactive Rules (${inactiveRules.length})`} />
          <Tab label="Performance" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          {activeRules.map((rule) => (
            <Grid item xs={12} md={6} lg={4} key={rule.id}>
              <PricingRuleCard
                rule={rule}
                onEdit={handleEditRule}
                onToggle={handleToggleRule}
                onDelete={handleDeleteRule}
              />
            </Grid>
          ))}
          {activeRules.length === 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="h6" color="textSecondary">
                  No active pricing rules
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  Create your first pricing rule to automate price adjustments
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<Add />}
                  onClick={handleAddRule}
                  sx={{ mt: 2 }}
                >
                  Create Rule
                </Button>
              </Paper>
            </Grid>
          )}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          {inactiveRules.map((rule) => (
            <Grid item xs={12} md={6} lg={4} key={rule.id}>
              <PricingRuleCard
                rule={rule}
                onEdit={handleEditRule}
                onToggle={handleToggleRule}
                onDelete={handleDeleteRule}
              />
            </Grid>
          ))}
          {inactiveRules.length === 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="h6" color="textSecondary">
                  No inactive rules
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  All your pricing rules are currently active
                </Typography>
              </Paper>
            </Grid>
          )}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Pricing Performance Overview
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                Track the impact of your pricing rules on revenue and margins
              </Typography>
              {/* Here you would add charts showing pricing performance */}
              <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'grey.100' }}>
                <Typography variant="body2" color="textSecondary">
                  Performance charts will be displayed here
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
                    primary="Total Revenue Impact"
                    secondary={
                      <Typography color="success.main">
                        +15.2% this month
                      </Typography>
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Average Margin"
                    secondary={
                      <Typography color="success.main">
                        +4.8% improvement
                      </Typography>
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Rules Triggered"
                    secondary="127 times today"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Price Adjustments"
                    secondary="89 products updated"
                  />
                </ListItem>
              </List>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      <PricingRuleDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        rule={selectedRule}
        onSave={handleSaveRule}
      />
    </Box>
  );
}

export default Pricing;
