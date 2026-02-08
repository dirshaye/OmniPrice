import React, { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  TextField,
  Typography,
} from '@mui/material';
import { llmAPI } from '../../services/api';

function LLMPlayground() {
  const [prompt, setPrompt] = useState('');
  const [context, setContext] = useState('');
  const [model, setModel] = useState('gemini-flash-latest');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    setResponse('');

    try {
      const res = await llmAPI.ask({
        prompt,
        context: context || null,
        model,
      });
      setResponse(res.data.response || '');
    } catch (err) {
      setError(err.response?.data?.detail || 'LLM request failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" gutterBottom>
        LLM Playground
      </Typography>
      <Paper sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Model</InputLabel>
            <Select value={model} label="Model" onChange={(e) => setModel(e.target.value)}>
              <MenuItem value="gemini-flash-latest">Gemini Flash (latest)</MenuItem>
              <MenuItem value="gemini-2.0-flash">Gemini 2.0 Flash</MenuItem>
              <MenuItem value="gemini-2.5-flash">Gemini 2.5 Flash</MenuItem>
              <MenuItem value="gemini-2.5-pro">Gemini 2.5 Pro</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            multiline
            minRows={3}
            sx={{ mb: 2 }}
            required
          />
          <TextField
            fullWidth
            label="Context (optional)"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            multiline
            minRows={3}
            sx={{ mb: 2 }}
          />
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? 'Running...' : 'Ask LLM'}
          </Button>
        </form>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {response && (
        <Paper sx={{ p: 3, mt: 2 }}>
          <Typography variant="h6" gutterBottom>
            Response
          </Typography>
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {response}
          </Typography>
        </Paper>
      )}
    </Box>
  );
}

export default LLMPlayground;
