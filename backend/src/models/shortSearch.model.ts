import mongoose, { Schema, Document } from "mongoose";

interface ShortSearchLogSchema extends Document {
    query: string;
    timestamp: Date;
}

const ShortSearchLogSchema: Schema = new Schema({
    query: { type: String, required: true },
    timestamp: { type: Date, default: Date.now }
});

export default mongoose.model<ShortSearchLogSchema>('SearchLog', ShortSearchLogSchema);