import mongoose, { Schema, Document } from "mongoose";

interface SearchLogSchema extends Document {
    query: string;
    timestamp: Date;
}

const SearchLogSchema: Schema = new Schema({
    query: { type: String, required: true },
    timestamp: { type: Date, default: Date.now }
});

export default mongoose.model<SearchLogSchema>('searchLog', SearchLogSchema);