import mongoose, { Schema, Document } from "mongoose";

interface longSearchLogSchema extends Document {
    query: string;
    timestamp: Date;
}

const longSearchLogSchema: Schema = new Schema({
    query: { type: String, required: true },
    timestamp: { type: Date, default: Date.now }
});

export default mongoose.model<longSearchLogSchema>('longSearchLog', longSearchLogSchema);