import { Router } from 'express';
import axios from 'axios';
import SearchLog from '../models/search.model';

const router = Router();

router.get('/', async (req, res) => {
    try {
        // const query = req.query.query as string;
        const query = "Humans"
        if (!query) {
            return res.status(400).json({ error: 'Query parameter is required' });
        }

        // Hit Wikipedia's search API
        const wikiResponse = await axios.get('https://en.wikipedia.org/w/api.php', {
            params: {
                action: 'query',
                list: 'search',
                srsearch: query,    
                format: 'json',
                origin: '*'
            }
        });

        console.log('Wikipedia response:', wikiResponse.data);

        // Save search log to DB
        await SearchLog.create({ query, timestamp: new Date() });

        // Wikipedia returns data under data.query.search
        const searchResults = wikiResponse.data.query?.search || [];
        console.log('Search results:', searchResults);

        res.json({ results: searchResults });
    } catch (error: any) {
        console.error('Error searching Wikipedia:', error.message);
        res.status(500).json({ error: 'Internal server error' });
    }
});

export default router;
