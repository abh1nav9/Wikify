const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');

import { connectDB } from './connection';
import searchRoutes from './routes/search.route';

dotenv.config();
const app = express();

connectDB();

app.use(cors());
app.use(express.json());

app.use('/v1/search', searchRoutes);

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
