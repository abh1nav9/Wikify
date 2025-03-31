import { Router } from 'express';
import { searchQuery } from '../controllers/search.controller';

const router = Router();

router.get('/', searchQuery);

export default router;
