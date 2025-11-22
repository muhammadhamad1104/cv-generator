# CV Generator MCP Server (Python)

**Standalone** Python implementation of the CV Generator MCP (Model Context Protocol) server. Generates professional CVs directly without external dependencies.

## ✨ Features

- **Standalone PDF Generation**: Uses WeasyPrint - no backend required
- **Complete Profile CRUD**: Create, read, update, delete profiles
- **Three Professional Templates**: Classic, Modern, Europass
- **MongoDB Integration**: Async database operations with Motor
- **FastMCP Cloud Ready**: Deploy directly to FastMCP cloud

## 📂 Structure

```
cv-generator/
├── server.py              # Main MCP server
├── client.py              # Interactive test client
├── verify.py              # Setup verification
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
├── config/
│   └── database.py        # MongoDB connection
├── models/
│   ├── profile.py         # Profile schema
│   ├── cv.py              # CV schema
│   └── user.py            # User schema
├── services/
│   ├── cv_service.py      # Standalone PDF generation
│   └── storage_service.py # Local file storage
├── templates/
│   └── cv/
│       ├── classic.hbs    # Classic template + CSS
│       ├── classic.css
│       ├── modern.hbs     # Modern template + CSS
│       ├── modern.css
│       ├── europass.hbs   # Europass template + CSS
│       └── europass.css
├── tools/
│   ├── generate_cv.py     # CV generation tool
│   └── profile_tools.py   # Profile CRUD tools
└── uploads/
    └── cv/                # Generated PDFs
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd cv-generator
pip install -r requirements.txt
```

### 2. Configure Environment

Update `.env` with your MongoDB connection:
```env
MONGO_URI=mongodb+srv://your-connection-string
```

### 3. Verify Setup

```bash
python verify.py
```

This checks:
- ✅ All files present
- ✅ Python packages installed (WeasyPrint, Pybars3, Motor)
- ✅ Environment configured
- ✅ Tools loaded correctly

### 4. Run the Server

```bash
python server.py
```

### 5. Test with Client

```bash
python client.py
```

## 🔧 Configuration

The server requires only MongoDB. Configure in `.env`:

```env
# MongoDB Connection (MongoDB Atlas or local)
MONGO_URI=mongodb+srv://...

# Environment
NODE_ENV=production
```

## 🛠️ Available Tools

### 1. `generate_cv`

Generate a professional CV from user profile data.

**Parameters:**
- `userId` (required): User ID
- `template` (optional): CV template (classic, modern, europass) - default: "europass"
- `cvId` (optional): Existing CV ID to regenerate
- `settings` (optional): Customization settings

**Example:**
```json
{
  "userId": "507f1f77bcf86cd799439011",
  "template": "europass",
  "settings": {
    "color": "#2E5090",
    "fontSize": 12,
    "sections": {
      "personalInfo": true,
      "workExperience": true,
      "education": true
    }
  }
}
```

### 2. `get_profile`

Retrieve a user profile by userId.

**Parameters:**
- `userId` (required): User ID

**Example:**
```json
{
  "userId": "507f1f77bcf86cd799439011"
}
```

### 3. `create_profile`

Create a new user profile.

**Parameters:**
- `userId` (required): User ID
- `personalInfo` (required): Personal information object
- `summary` (optional): Professional summary
- `workExperience` (optional): Array of work experiences
- `education` (optional): Array of education entries
- `skills` (optional): Array of skills
- `languages` (optional): Array of languages
- `certifications` (optional): Array of certifications
- `projects` (optional): Array of projects
- `socialLinks` (optional): Social media links object

**Example:**
```json
{
  "userId": "507f1f77bcf86cd799439011",
  "personalInfo": {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "city": "New York",
    "country": "USA"
  },
  "summary": "Experienced software engineer...",
  "skills": [
    {"name": "Python", "level": "Expert"},
    {"name": "JavaScript", "level": "Advanced"}
  ]
}
```

### 4. `update_profile`

Update an existing user profile. Merges provided fields with existing data.

**Parameters:**
- `userId` (required): User ID
- Any profile fields to update (same as create_profile)

**Example:**
```json
{
  "userId": "507f1f77bcf86cd799439011",
  "summary": "Updated professional summary",
  "skills": [
    {"name": "Python", "level": "Expert"},
    {"name": "Go", "level": "Intermediate"}
  ]
}
```

### 5. `delete_profile`

Delete a user profile completely.

**Parameters:**
- `userId` (required): User ID

**Example:**
```json
{
  "userId": "507f1f77bcf86cd799439011"
}
```

## 🔄 How It Works

1. **MCP Server** receives tool calls via stdio
2. **Tools** process the requests:
   - `generate_cv`: Validates data → generates PDF → saves to MongoDB
   - `get_profile`: Retrieves profile from MongoDB
   - `create_profile`: Creates new profile in MongoDB
   - `update_profile`: Updates existing profile
   - `delete_profile`: Deletes profile from MongoDB
3. **Services** handle business logic:
   - `cv_service`: Validates data, generates PDF using WeasyPrint (standalone)
   - `storage_service`: Saves generated files to `uploads/cv/`
4. **Database** (MongoDB): Stores profiles, CV metadata
5. **PDF Generation**: WeasyPrint renders Handlebars templates to PDF (no external dependencies)

## 📦 Deployment

### Local Development

1. **Install Dependencies:**
```bash
cd cv-generator
pip install -r requirements.txt
```

2. **Configure Environment:**
Edit `.env`:
```env
MONGO_URI=mongodb+srv://your-connection-string
NODE_ENV=production
```

3. **Test MCP Server:**
```bash
python verify.py  # Check setup
python client.py  # Interactive testing
```

### FastMCP Cloud Deployment

To deploy on FastMCP cloud:

1. **Prepare Dependencies:**
Ensure `requirements.txt` is complete (already done)

2. **Environment Variables:**
Set in FastMCP dashboard:
- `MONGO_URI`: Your MongoDB Atlas connection string
- `NODE_ENV`: production

3. **Entry Point:**
The server uses stdio transport - FastMCP will handle this automatically
- Main file: `server.py`
- Command: `python server.py`

4. **Important Notes:**
- Completely standalone - no backend required
- MongoDB Atlas recommended for cloud deployment
- Templates are embedded in `templates/cv/` directory
- PDFs generated using WeasyPrint (native Python)

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

#### For Local Development:
```json
{
  "mcpServers": {
    "cv-generator": {
      "command": "python",
      "args": ["d:\\ALL SEMESTER\\CV_Generator\\cv-generator\\server.py"],
      "env": {
        "MONGO_URI": "your-mongodb-uri"
      }
    }
  }
}
```

#### For FastMCP Cloud:
```json
{
  "mcpServers": {
    "cv-generator": {
      "command": "fastmcp",
      "args": ["your-fastmcp-deployment-url"],
      "env": {}
    }
  }
}
```

## 🎨 Templates

The Python MCP server includes three professional CV templates (same as Node.js version):

### 1. **Classic Template** (`classic`)
- Two-column layout (sidebar + main content)
- Professional blue color scheme
- Compact and information-dense
- Perfect for: Traditional industries, academic positions

### 2. **Modern Template** (`modern`)
- Clean, contemporary design
- Horizontal header layout
- More spacious and readable
- Perfect for: Tech companies, creative roles, startups

### 3. **Europass Template** (`europass`)
- Based on European CV standard
- Blue gradient sidebar
- Skills with visual proficiency bars
- Perfect for: EU job applications, international positions

**Template Files:**
```
templates/cv/
├── classic.hbs & classic.css
├── modern.hbs & modern.css
└── europass.hbs & europass.css
```

**Usage:**
```python
# When calling generate_cv tool
{
  "userId": "...",
  "template": "modern",  # or "classic" or "europass"
  "settings": { ... }
}
```

All templates support:
- ✅ Profile photos (optional)
- ✅ Personal information
- ✅ Work experience with dates
- ✅ Education history
- ✅ Skills with proficiency levels
- ✅ Languages (CEFR levels for Europass)
- ✅ Certifications & memberships
- ✅ Social links (LinkedIn, GitHub, Portfolio)
- ✅ Projects (Modern template)
- ✅ References (Modern template)

## 🆚 Node.js vs Python

| Feature | Node.js | Python |
|---------|---------|--------|
| MCP SDK | ✅ `@modelcontextprotocol/sdk` | ✅ `mcp` |
| Database | MongoDB (Mongoose) | MongoDB (Motor) |
| PDF Generation | Puppeteer | Calls Node.js backend API |
| Transport | stdio | stdio |
| Async | Promises/async-await | asyncio/async-await |

Both implementations:
- ✅ Same MCP protocol
- ✅ Same tool interface
- ✅ Same database
- ✅ Same functionality

## 🧪 Testing

### Test with MCP Inspector

```bash
# Install MCP inspector
npm install -g @modelcontextprotocol/inspector

# Run with inspector
mcp-inspector python server.py
```

### Test with Claude Desktop

Add to Claude Desktop config (`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "cv-generator-python": {
      "command": "python",
      "args": ["d:\\ALL SEMESTER\\CV_Generator\\mcp-python\\server.py"],
      "env": {
        "MONGO_URI": "your-mongodb-uri"
      }
    }
  }
}
```

## 📝 Development

### Adding New Tools

1. Create a new tool class in `tools/`:
```python
class MyNewTool:
    def __init__(self):
        self.name = 'my_tool'
        self.description = 'What it does'
        self.input_schema = { ... }
    
    async def execute(self, args):
        # Implementation
        return result
```

2. Register in `server.py`:
```python
self.tools = [GenerateCVTool(), MyNewTool()]
```

### Adding New Services

Create service classes in `services/` for business logic.

## 🔒 Security Notes

- Environment variables should be kept secure
- MongoDB connection strings contain credentials
- The server runs on stdio (secure by design)
- File paths are validated before storage

## 🐛 Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Connection refused"
- Ensure MongoDB is accessible
- Check `MONGO_URI` in `.env`
- Verify network connectivity

### "Backend API error"
- Ensure Node.js backend is running on port 3000
- Check `BACKEND_URL` in `.env`

### "Tool not found"
- Check tool registration in `server.py`
- Verify tool name matches exactly

## 📚 Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Motor (Async MongoDB)](https://motor.readthedocs.io/)

## 🤝 Comparison with Node.js Version

This Python implementation mirrors the Node.js version in `backend/src/mcp/`. Both:

- Use the same MCP protocol
- Connect to the same MongoDB database
- Provide the same `generate_cv` tool
- Return the same response format

Choose based on your preference:
- **Node.js**: If you prefer JavaScript/TypeScript ecosystem
- **Python**: If you prefer Python ecosystem or want to extend with Python libraries

## 📄 License

Same as main CV Generator project.
