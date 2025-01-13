const express = require('express');
const cors = require('cors');
import { PORT } from './proxy';

import { connectDB } from './connection';
import searchRoutes from './routes/search.route';

const app = express();

connectDB();

app.use(cors());
app.use(express.json());

app.use('/v1/search', searchRoutes);

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
