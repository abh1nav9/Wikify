import { Request, Response } from 'express';
import axios from 'axios';
import ShortSearchLogSchema from '../models/shortSearch.model';

export async function shortSearchQuery(req: Request, res: Response) {
    try {
        const query = req.query.query as string;
        if (!query) {
            return res.status(400).json({ error: 'Query parameter is required' });
        }

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

        // console.log('Wikipedia response:', wikiResponse.data);

        // Save the search log to the database
        await ShortSearchLogSchema.create({ query, timestamp: new Date() });

        // Return the result from Wikipedia
        res.json({ results: wikiResponse.data });
    } catch (error: any) {
        console.error('Error searching Wikipedia:', error.message);
        res.status(500).json({ error: 'Internal server error' });
    }
}
