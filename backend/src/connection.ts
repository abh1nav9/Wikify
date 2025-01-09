import mongoose from 'mongoose';
import {MONGO_URI} from './proxy';

const MONGODB_URI = MONGO_URI || "String Not Available";

export const connectDB = async () => {
  try {
    await mongoose.connect(MONGODB_URI);
    console.log('Connected to MongoDB');
  } catch (error) {
    console.error('MongoDB connection error:', error);
    process.exit(1);
  }
};
