import { Request, Response } from 'express';
import axios from 'axios';
import SearchLog from '../models/search.model';

export async function searchQuery(req: Request, res: Response) {
    try {
        const query = req.query.query as string;
        if (!query) {
            return res.status(400).json({ error: 'Query parameter is required' });
        }

        // Use the correct Wikipedia API endpoint with the provided query
        const wikiResponse = await axios.get('https://en.wikipedia.org/w/api.php', {
            params: {
                action: 'query',
                format: 'json',
                prop: 'extracts',
                titles: query,
                formatversion: 2,
                exsentences: 10,
                exlimit: 1,
                explaintext: 1,
            }
        });

        console.log('Wikipedia response:', wikiResponse.data);

        // Save the search log to the database
        await SearchLog.create({ query, timestamp: new Date() });

        // Return the result from Wikipedia
        res.json({ results: wikiResponse.data });
    } catch (error: any) {
        console.error('Error searching Wikipedia:', error.message);
        res.status(500).json({ error: 'Internal server error' });
    }
}
