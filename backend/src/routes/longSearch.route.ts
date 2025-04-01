import { Router } from 'express';
import { longSearchQuery } from '../controllers/longSearch.controller';

const router = Router();

router.get('/', longSearchQuery);

export default router;