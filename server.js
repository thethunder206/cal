const express = require('express');
const cors = require('cors');
const { google } = require('googleapis');

const app = express();
app.use(cors());

const CLIENT_ID = '357347057692-lpmistphf2al5cqfttgvmbmhjobb9hgk.apps.googleusercontent.com';
const CLIENT_SECRET = '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';
const REDIRECT_URI = 'https://cal-2.onrender.com/oauth/callback';

const oauth2Client = new google.auth.OAuth2(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI);

app.get('/auth/google', (req, res) => {
    const authUrl = oauth2Client.generateAuthUrl({
        access_type: 'offline',
        scope: ['https://www.googleapis.com/auth/calendar.readonly'],
    });
    res.redirect(authUrl);
});

app.get('/oauth/callback', async (req, res) => {
    try {
        const { code } = req.query;
        const { tokens } = await oauth2Client.getToken(code);
        oauth2Client.setCredentials(tokens);

        // Redirect back to WeChat Mini Program with token
        const redirectURL = `weixin://custom-url?token=${tokens.access_token}`;
        res.redirect(redirectURL);
    } catch (error) {
        res.status(500).send('Authentication failed');
    }
});

app.get('/calendar', async (req, res) => {
    try {
        const token = req.query.token;
        if (!token) return res.status(401).json({ error: 'No token provided' });

        oauth2Client.setCredentials({ access_token: token });

        const calendar = google.calendar({ version: 'v3', auth: oauth2Client });
        const events = await calendar.events.list({
            calendarId: 'primary',
            timeMin: new Date().toISOString(),
            maxResults: 10,
            singleEvents: true,
            orderBy: 'startTime',
        });

        res.json(events.data.items);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch calendar events' });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
