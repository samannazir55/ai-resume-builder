
# IMMORTAL TEMPLATES CONFIG
# This file regenerates the database if it ever gets wiped.

PERMANENT_TEMPLATES = [
    {
        "id": "modern",
        "name": "Modern Blue",
        "category": "professional",
        "is_premium": False,
        "html": "<div class='resume-modern'><div class='sidebar'><div class='profile-container'>{{#profile_image}}<img src='{{profile_image}}' class='profile-img'/>{{/profile_image}}<h1>{{full_name}}</h1><p class='job-title'>{{job_title}}</p></div><div class='contact-box'><div class='label'>Contact</div><div class='value'>{{email}}</div><div class='value'>{{phone}}</div></div><div class='skills-box'><div class='label'>Skills</div><ul>{{#skills}}<li>{{.}}</li>{{/skills}}</ul></div></div><div class='main-content'><div class='section'><h2>Profile</h2><div class='text'>{{{summary}}}</div></div><div class='section'><h2>Experience</h2><div class='text history-list'>{{{experience}}}</div></div><div class='section'><h2>Education</h2><div class='text history-list'>{{{education}}}</div></div></div></div>",
        "css": ".resume-modern{display:flex;font-family:sans-serif;height:100%;min-height:1000px;background:white;color:#333}.sidebar{width:35%;background:var(--primary, #2c3e50);color:white;padding:30px 20px;text-align:center}.main-content{width:65%;padding:30px}.profile-img{width:120px;height:120px;border-radius:50%;border:4px solid rgba(255,255,255,0.2);object-fit:cover;margin-bottom:10px}h1{font-size:22px;margin:10px 0 5px 0;text-transform:uppercase}.job-title{font-size:14px;opacity:0.9;margin-bottom:30px}.label{font-weight:bold;text-transform:uppercase;border-bottom:1px solid rgba(255,255,255,0.2);padding-bottom:5px;margin:20px 0 10px 0;font-size:12px}.skills-box li{background:rgba(0,0,0,0.2);margin-bottom:5px;padding:5px;border-radius:3px;font-size:12px}h2{color:var(--primary, #2c3e50);border-bottom:2px solid var(--primary, #2c3e50);padding-bottom:5px;text-transform:uppercase;margin-top:0}.text{font-size:14px;line-height:1.6;margin-bottom:20px} .history-list p { margin:5px 0; }"
    },
    {
        "id": "classic",
        "name": "Classic Clean",
        "category": "simple",
        "is_premium": False,
        "html": "<div class='resume-classic'><div class='header'><h1>{{full_name}}</h1><p>{{job_title}}</p><p class='contact'>{{email}} | {{phone}}</p></div><hr/><h3>Professional Summary</h3><p class='summary'>{{{summary}}}</p><h3>Skills</h3><div class='skills-grid'>{{#skills}}<span class='skill-item'>{{.}}</span>{{/skills}}</div><h3>Experience</h3><div class='content'>{{{experience}}}</div><h3>Education</h3><div class='content'>{{{education}}}</div></div>",
        "css": ".resume-classic{font-family:'Times New Roman',serif;padding:40px;background:white;color:#000;min-height:1000px}.header{text-align:center;margin-bottom:20px}h1{margin:0;font-size:28px;text-transform:uppercase;letter-spacing:2px}.header p{margin:5px 0;font-style:italic}h3{background:#f0f0f0;padding:5px 10px;text-transform:uppercase;font-size:14px;font-weight:bold;border-left:5px solid #333;margin-top:20px}.skills-grid{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:20px}.skill-item{border:1px solid #333;padding:3px 8px;font-size:13px}ul{padding-left:20px}"
    },
    {
        "id": "startup_bold",
        "name": "Startup Bold",
        "category": "creative",
        "is_premium": True,
        "html": "<div class='resume-start'><div class='start-sidebar'><h1>{{full_name}}</h1><h3>{{job_title}}</h3>{{#profile_image}}<div class='start-img-container'><img src='{{profile_image}}'/></div>{{/profile_image}}<div class='start-group'><div class='start-label'>Contact</div><div>{{email}}</div><div>{{phone}}</div></div><div class='start-group'><div class='start-label'>Skills</div><div class='tag-cloud'>{{#skills}}<span class='tag'>{{.}}</span>{{/skills}}</div></div></div><div class='start-body'><h2 class='shadow-head'>Manifesto</h2><div class='content'>{{{summary}}}</div><h2 class='shadow-head'>Experience</h2><div class='content'>{{{experience}}}</div><h2 class='shadow-head'>Education</h2><div class='content'>{{{education}}}</div></div></div>",
        "css": ":root{--primary: {{accent_color}};} .resume-start{display:flex;font-family:sans-serif;min-height:1000px;background:#fff;width:100%;overflow:hidden;}.start-sidebar{width:30%;min-width:250px;background:#111;color:white;padding:40px 20px;text-align:center;box-sizing:border-box}.start-body{width:70%;padding:40px;box-sizing:border-box}h1{font-size:32px;margin:0 0 10px 0;line-height:1.1}h3{font-size:16px;font-weight:300;opacity:0.8;color:var(--primary);text-transform:uppercase;letter-spacing:1px}.start-img-container img{width:150px!important;height:150px!important;border-radius:50%;border:4px solid var(--primary);object-fit:cover;margin:0 auto 30px auto;display:block}.start-label{font-size:11px;text-transform:uppercase;color:#888;border-bottom:1px solid #333;margin-bottom:5px}.tag{display:inline-block;background:#333;padding:4px 8px;border-radius:4px;margin:2px;font-size:11px}.shadow-head{font-size:24px;color:#333;text-transform:uppercase;font-weight:800;border-left:5px solid var(--primary);padding-left:15px;margin:0 0 20px 0}"
    }
]
