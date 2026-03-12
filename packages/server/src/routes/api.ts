import { Router } from 'express';

const router: Router = Router();

router.get('/health', (_req, res) => {
  res.json({ ok: true });
});

export default router;
