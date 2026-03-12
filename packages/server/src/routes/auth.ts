import { Router, Request, Response } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { getDb } from '../db/connection.js';
import { authRequired } from '../middleware/auth.js';
import { config } from '../config.js';

const now = () => new Date().toISOString().replace('T', ' ').slice(0, 19);
const router: Router = Router();

router.post('/login', (req: Request, res: Response) => {
  try {
    const { username, password } = req.body ?? {};
    if (!username || !password) {
      res.status(400).json({ error: 'Username and password are required' });
      return;
    }

    const db = getDb();
    const user = db.prepare(
      'SELECT id, username, password_hash, must_change_password FROM admin_user WHERE username = ?'
    ).get(username) as { id: number; username: string; password_hash: string; must_change_password: number } | undefined;

    if (!user || !bcrypt.compareSync(password, user.password_hash)) {
      res.status(401).json({ error: 'Invalid username or password' });
      return;
    }

    const token = jwt.sign(
      { userId: user.id, username: user.username },
      config.JWT_SECRET,
      { expiresIn: '7d' }
    );

    res.status(200).json({
      token,
      userId: user.id,
      username: user.username,
      mustChangePassword: Boolean(user.must_change_password),
    });
  } catch (err) {
    console.error('Login error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.post('/change-password', authRequired, (req: Request, res: Response) => {
  try {
    const { oldPassword, newPassword } = req.body ?? {};
    if (!oldPassword || !newPassword) {
      res.status(400).json({ error: 'Old password and new password are required' });
      return;
    }

    const userId = (req as Request & { userId?: number }).userId;
    if (!userId) {
      res.status(401).json({ error: 'Unauthorized' });
      return;
    }

    const db = getDb();
    const user = db.prepare(
      'SELECT id, password_hash FROM admin_user WHERE id = ?'
    ).get(userId) as { id: number; password_hash: string } | undefined;

    if (!user || !bcrypt.compareSync(oldPassword, user.password_hash)) {
      res.status(400).json({ error: 'Invalid old password' });
      return;
    }

    const passwordHash = bcrypt.hashSync(newPassword, 10);
    db.prepare(
      'UPDATE admin_user SET password_hash = ?, must_change_password = 0 WHERE id = ?'
    ).run(passwordHash, userId);

    res.status(200).json({ message: 'Password changed successfully' });
  } catch (err) {
    console.error('Change password error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
