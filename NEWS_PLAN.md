# OSRS News Aggregation Plan

## Overview
Build a news aggregation feature that pulls OSRS news from official blog posts and top Reddit posts, stores them in the database, and displays them on the frontend.

## Architecture

### Backend (API)
- **News fetcher service**: Periodically fetch news from multiple sources
- **Database storage**: Store news items with metadata
- **API endpoints**: Serve aggregated news to frontend

### Frontend
- **News page/component**: Display aggregated news feed
- **News item cards**: Show individual news items with source, title, date, preview

## Data Sources

### 1. OSRS Official Blog
- URL: `https://secure.runescape.com/m=news/latest_news.rss?oldschool=true` (RSS feed)
- Alternative: Scrape from `https://secure.runescape.com/m=news/latest_news`
- Data to extract:
  - Title
  - Publication date
  - Summary/preview text
  - Link to full article
  - Categories/tags (if available)

### 2. Reddit (/r/2007scape)
- URL: `https://www.reddit.com/r/2007scape/top.json?t=week`
- Use Reddit's JSON API (no auth needed for public posts)
- Data to extract:
  - Post title
  - Author
  - Score (upvotes)
  - Number of comments
  - Posted date
  - Link/URL
  - Post flair (News, Discussion, etc.)
  - Thumbnail (if available)

## Database Schema

### News Table
```sql
CREATE TABLE news (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,  -- 'osrs_blog' or 'reddit'
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    published_date DATETIME NOT NULL,
    preview_text TEXT,
    author TEXT,  -- For Reddit posts
    score INTEGER,  -- For Reddit posts (upvotes)
    comment_count INTEGER,  -- For Reddit posts
    flair TEXT,  -- For Reddit posts
    thumbnail_url TEXT,  -- For Reddit posts
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_news_published_date ON news(published_date DESC);
CREATE INDEX idx_news_source ON news(source);
```

## Implementation Steps

### Phase 1: Backend - Data Fetching
1. Create news fetcher module (`api/news_fetcher.py`)
   - OSRS blog RSS parser
   - Reddit JSON API client
   - Error handling and retry logic

2. Create database models (`api/models/news.py`)
   - News model with SQLAlchemy
   - Migration script

3. Create news service (`api/services/news_service.py`)
   - Fetch and store news from both sources
   - Deduplicate entries
   - Update existing entries if needed

### Phase 2: Backend - API Endpoints
1. Add news endpoints (`api/routes/news.py`)
   - `GET /api/news` - Get paginated news feed
     - Query params: `?limit=20&offset=0&source=all|osrs_blog|reddit`
   - `GET /api/news/:id` - Get single news item
   - `POST /api/news/refresh` - Manually trigger news fetch (admin)

### Phase 3: Scheduled Fetching
1. Add background job/scheduler
   - Fetch news every 30 minutes or 1 hour
   - Options: APScheduler, Celery, or simple cron job
   - Log fetch results and errors

### Phase 4: Frontend - News Display
1. Create news page (`frontend/src/views/NewsView.vue`)
   - Grid/list layout for news items
   - Filter by source (All, Blog, Reddit)
   - Pagination or infinite scroll

2. Create news components
   - `NewsCard.vue` - Individual news item card
   - `NewsFilter.vue` - Source filter buttons
   - Different styles for blog vs Reddit posts

3. Add API client methods (`frontend/src/api/news.ts`)
   - fetchNews()
   - fetchNewsById()

4. Add to navigation/routing

## Technical Considerations

### API Rate Limiting
- Reddit API: ~60 requests/min (no auth), be respectful
- OSRS blog: No known limits, but cache responses
- Implement exponential backoff for failures

### Caching
- Cache news data in database
- Only fetch new posts since last update
- Consider adding Redis cache for API responses

### Error Handling
- Handle network failures gracefully
- Log errors for debugging
- Show cached data if fetch fails
- Display source status on frontend (last updated time)

### Data Freshness
- Show "posted X hours ago" timestamps
- Highlight new posts (posted in last 24h)
- Archive or hide posts older than 30 days

### Content Filtering
- Filter Reddit posts by flair (e.g., only News, JMod Reply)
- Minimum score threshold for Reddit posts (e.g., >100 upvotes)
- Exclude certain post types (memes, if desired)

## Future Enhancements
- Push notifications for important news
- Email digest of weekly news
- Search functionality
- Save/bookmark favorite posts
- Comments integration
- RSS feed output from our API
- Twitter/X integration for @OldSchoolRS tweets
