const express = require('express');
const cors = require('cors');
import { PORT } from './proxy';

import { connectDB } from './connection';
import shortSearchRoutes from './routes/shortSearch.route';
import longSearchRoutes from './routes/longSearch.route';
import searchRoutes from './routes/search.route';

const app = express();

connectDB();

app.use(cors({ origin: 'http://localhost:5173' }));
app.use(express.json());

app.use('/v1/shortSearch', shortSearchRoutes);
app.use('/v1/longSearchWiki', longSearchRoutes);
app.use('/v1/search', searchRoutes);

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
