import mongoose from 'mongoose';
import {MONGO_URI} from './proxy';


export const connectDB = async () => {
  try {
    if (!MONGO_URI) {
      throw new Error('MONGODB_URI is not defined');
    }
    await mongoose.connect(MONGO_URI);
    console.log('Connected to MongoDB');
  } catch (error) {
    console.error('MongoDB connection error:', error);
    process.exit(1);
  }
};
