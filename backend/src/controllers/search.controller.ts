import { Request, Response } from 'express';
import axios from 'axios';
import searchModel from '../models/search.model';

export async function searchQuery(req: Request, res: Response) {
    try {
        const query = req.query.query as string;
        if (!query) {
            return res.status(400).json({ error: 'Query parameter is required' });
        }
        const wikiResponse = await axios.get('https://en.wikipedia.org/w/rest.php/v1/search/title', {
            params: {
                q: query,
                limit: 10
            }
        });

        // Save the search log to the database
        await searchModel.create({ query, timestamp: new Date() });

        // Return the result from Wikipedia
        res.json({ results: wikiResponse.data });
    }
    catch (error: any) {
        console.error('Error searching Wikipedia:', error.message);
        res.status(500).json({ error: 'Internal server error' });
    }
};