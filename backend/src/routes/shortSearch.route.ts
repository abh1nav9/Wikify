import { Router } from 'express';
import { shortSearchQuery } from '../controllers/shortSearch.controller';

const router = Router();

router.get('/', shortSearchQuery);

export default router;
