# server/scripts/add_full_articles.py
"""
מוסיף מאמרים עם תוכן מלא באנגלית
"""

import sys
import os
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.mvc.models.articles.article_entity import Article


FULL_ARTICLES = [
    {
        "title": "AI Breakthrough: New Model Understands Context Like Humans",
        "summary": "Stanford researchers develop revolutionary AI model that can understand emotional context in conversations nearly as well as humans.",
        "content": """
Stanford University researchers have unveiled a groundbreaking artificial intelligence model that represents a major leap forward in natural language understanding. The new system, called "ContextPro," can comprehend subtle emotional nuances and contextual cues in human conversation with unprecedented accuracy.

The Development Process

The research team spent three years training the model on millions of real human conversations, spanning casual chats, professional communications, therapy sessions, and customer service interactions. This diverse dataset allowed the AI to learn the intricate ways humans convey meaning beyond literal words.

"Traditional AI models excel at understanding explicit statements but struggle with implicit communication," explains Dr. Sarah Chen, lead researcher on the project. "Humans constantly use sarcasm, implied meanings, and cultural references. Our model has learned to navigate this complexity."

Key Capabilities

The ContextPro system demonstrates several remarkable abilities that set it apart from previous AI models:

Sarcasm Detection: The model achieved 94% accuracy in identifying sarcastic statements, compared to 87% for previous state-of-the-art systems. This improvement came from analyzing vocal tone patterns, punctuation usage, and contextual contradictions.

Emotional Intelligence: ContextPro can identify subtle emotional states like frustration masking sadness, or enthusiasm hiding anxiety. This nuanced understanding could revolutionize mental health support systems and customer service applications.

Cultural Awareness: The model was trained on conversations from 47 different cultural contexts, allowing it to understand idioms, references, and communication styles across diverse populations.

Intent Recognition: Beyond understanding what someone says, the system can infer why they're saying it, recognizing hidden intentions and unspoken concerns.

Technical Innovation

The breakthrough came from a novel neural architecture that mimics how human brains process social information. The system uses multiple processing layers:

A primary layer analyzes literal content
Secondary layers evaluate tone, timing, and context
A metacognitive layer integrates all information to form holistic understanding

This multi-layered approach allows the AI to catch contradictions between what's said and what's meant, similar to how humans detect when someone says "I'm fine" but clearly isn't.

Real-World Applications

The potential applications for this technology are extensive:

Mental Health Support: AI therapists could provide more empathetic, contextually-aware support for people seeking help. The system could detect warning signs of crisis even when patients don't explicitly express distress.

Customer Service: Automated systems could better understand frustrated customers and respond appropriately, potentially de-escalating situations that would otherwise require human intervention.

Education: Intelligent tutoring systems could recognize when students are confused or discouraged, adjusting their teaching approach accordingly.

Accessibility: People with social communication difficulties could use the system as a tool to better understand others' intentions and emotions.

Ethical Considerations

The research team emphasizes the importance of responsible deployment. Dr. Chen notes, "With great power comes great responsibility. A system that understands human emotion this well could be misused for manipulation."

The team has implemented several safeguards:

Transparency requirements for all deployments
Strict privacy protections for training data
Built-in bias detection and correction systems
Human oversight protocols for sensitive applications

Industry Response

Major tech companies have already expressed interest in licensing the technology. Microsoft announced a partnership to integrate ContextPro into their communication platforms, while healthcare providers are exploring mental health applications.

However, some experts urge caution. Dr. James Morrison from the AI Ethics Institute warns, "We must ensure these systems enhance rather than replace human connection. There's a risk of over-relying on AI for emotional support."

The Road Ahead

The Stanford team plans to continue refining the model, with particular focus on:

Expanding cultural understanding to more languages and contexts
Improving real-time processing for live conversations
Developing safeguards against potential misuse
Creating open-source versions for research purposes

Future Implications

This advancement represents more than just better AI chatbots. It signals a new era where machines can truly understand the human experience, at least in certain dimensions. The implications extend to:

Human-AI Collaboration: Teams where AI assistants understand team dynamics and emotional states could be more productive and harmonious.

Social Research: Analyzing large-scale conversation data could reveal patterns in human communication previously invisible to researchers.

Cross-Cultural Communication: AI mediators could help bridge cultural communication gaps, facilitating better international cooperation.

Personal Development: Individuals could use the system to improve their own emotional intelligence by analyzing their communication patterns.

Conclusion

The ContextPro model represents a significant milestone in artificial intelligence development. By achieving near-human levels of contextual understanding, it opens doors to applications that seemed like science fiction just years ago.

However, the researchers emphasize that this technology should augment rather than replace human interaction. "AI can help us understand each other better," Dr. Chen concludes, "but nothing can replace genuine human connection."

As this technology moves from laboratory to real-world applications, society will need to grapple with questions about privacy, authenticity, and the nature of human connection in an increasingly AI-mediated world.
        """,
        "url": "https://example.com/ai-breakthrough-context",
        "source": "Stanford Tech Review",
        "category": "Technology",
        "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800",
        "thumb_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400"
    },
    {
        "title": "Mediterranean Diet Reduces Heart Disease Risk by 40%, Major Study Finds",
        "summary": "A comprehensive 12-year study of 10,000 participants reveals that Mediterranean diet significantly improves cardiovascular health.",
        "content": """
A landmark study published in the Journal of the American Medical Association (JAMA) has confirmed what nutritionists have long suspected: the Mediterranean diet substantially reduces the risk of heart disease and stroke.

The Study Design

Researchers followed 10,000 participants across 23 countries for 12 years, making this one of the largest and longest dietary intervention studies ever conducted. Participants were divided into three groups:

Traditional Mediterranean diet group
Low-fat diet group (control)
Standard diet group (control)

The Mediterranean diet group received regular counseling and resources to maintain a diet rich in olive oil, fish, vegetables, fruits, legumes, whole grains, and moderate wine consumption, while limiting red meat and processed foods.

Remarkable Results

The findings exceeded even optimistic expectations:

Cardiovascular Health: A 40% reduction in heart attack risk compared to the control groups. This represents one of the most significant dietary interventions ever documented.

Stroke Prevention: 35% lower incidence of stroke among Mediterranean diet followers. The protective effect was particularly strong for ischemic strokes.

Cholesterol Improvement: Average LDL (bad cholesterol) decreased by 28%, while HDL (good cholesterol) increased by 15%. This favorable shift in lipid profiles occurred without medication.

Blood Pressure: Systolic blood pressure decreased by an average of 15 points, reducing hypertension-related risks across the board.

Inflammation Markers: C-reactive protein and other inflammation markers dropped significantly, suggesting broader health benefits beyond cardiovascular protection.

The Science Behind the Benefits

Dr. Maria Rodriguez, lead researcher at the Barcelona Institute of Cardiovascular Research, explains the mechanisms: "The Mediterranean diet isn't just one factor—it's a synergistic combination of beneficial elements."

Olive Oil Benefits: Extra virgin olive oil contains polyphenols and monounsaturated fats that reduce inflammation and improve arterial function. The study found that participants consuming at least 4 tablespoons daily showed the strongest benefits.

Omega-3 Fatty Acids: Regular fish consumption (2-3 times weekly) provided essential omega-3s that reduce blood clotting, lower triglycerides, and stabilize heart rhythm.

Antioxidant Power: The high intake of colorful vegetables and fruits provided diverse antioxidants that protect blood vessels from oxidative damage.

Fiber Content: Whole grains, legumes, and vegetables delivered 35-40 grams of daily fiber, far exceeding typical Western diets. This fiber helps regulate cholesterol and blood sugar.

Gut Health: The diverse plant foods promoted healthy gut bacteria, which researchers increasingly recognize as crucial for cardiovascular health.

Beyond Heart Health

While cardiovascular benefits drove the study, researchers observed numerous additional effects:

Weight Management: Despite no calorie restrictions, Mediterranean diet participants maintained healthier weights. The average participant lost 8 pounds over the study period.

Diabetes Prevention: Type 2 diabetes incidence was 30% lower in the Mediterranean diet group, likely due to improved insulin sensitivity.

Cognitive Function: Preliminary data suggests better cognitive performance and lower dementia risk, though more research is needed.

Cancer Correlation: While not a primary study focus, researchers noted lower rates of certain cancers, particularly colorectal cancer.

Practical Implementation

The study's success partly stemmed from making the diet accessible and sustainable:

Gradual Transition: Participants weren't required to change everything overnight. They adopted Mediterranean principles over 3-6 months.

Cultural Adaptation: Researchers helped participants find Mediterranean diet equivalents within their own food cultures, making the approach more sustainable.

Meal Planning: Participants received practical meal plans and recipes, removing the guesswork from daily food choices.

Social Eating: The diet emphasized shared meals and mindful eating, reinforcing healthy habits through social connection.

Key Dietary Components

The successful participants focused on these core principles:

Olive Oil as Primary Fat: Replace butter, margarine, and vegetable oils with extra virgin olive oil for cooking and dressing.

Fish Over Red Meat: Aim for fish or seafood as the main protein 2-3 times weekly, with poultry for variety. Red meat should be limited to a few times monthly.

Plant-Based Foundation: Fill half your plate with vegetables, emphasizing variety and color. Include legumes (beans, lentils) several times weekly.

Whole Grains: Choose whole grain bread, brown rice, whole wheat pasta, and other minimally processed grains.

Nuts and Seeds: A daily handful (about 1 ounce) provides healthy fats, protein, and minerals.

Moderate Dairy: If consuming dairy, favor yogurt and cheese over milk, choosing quality over quantity.

Fresh Fruit: Enjoy fruit as dessert rather than sugary treats. The study participants averaged 2-3 servings daily.

Herbs and Spices: Use herbs and spices liberally for flavor instead of salt.

Expert Opinions

Dr. James Mitchell from Harvard Medical School, who wasn't involved in the study, calls the results "compelling evidence for dietary intervention as primary prevention."

"What's remarkable," he notes, "is that these benefits rival or exceed those of many pharmaceutical interventions, without the side effects. This should fundamentally change how we approach cardiovascular disease prevention."

However, he cautions against oversimplification: "The Mediterranean diet is a pattern, not a magic bullet. Success requires sustained lifestyle change, not just adding olive oil to an otherwise unhealthy diet."

Challenges and Considerations

Despite the impressive results, researchers acknowledge implementation challenges:

Cost Concerns: Fresh fish, quality olive oil, and abundant produce can be expensive. However, researchers note that reducing meat consumption can offset these costs.

Cultural Barriers: In some regions, Mediterranean staples aren't readily available or culturally familiar.

Time Investment: Preparing fresh meals requires more time than processed convenience foods.

Social Pressure: In cultures with different food norms, maintaining the diet can be socially challenging.

Recommendations for Adoption

Based on the study's success, researchers offer these tips for adopting Mediterranean eating:

Start Simple: Begin by adding one Mediterranean meal weekly, gradually increasing frequency.

Focus on Addition: Rather than thinking about restrictions, focus on adding beneficial foods.

Prep in Batches: Prepare large quantities of whole grains, roasted vegetables, or legume dishes to simplify weekday meals.

Make It Social: Share Mediterranean-style meals with family and friends to reinforce the habit.

Quality Over Perfection: Don't obsess over perfect adherence. The study participants who achieved 70-80% compliance still saw significant benefits.

Future Research Directions

The research team plans to continue following participants to assess long-term outcomes and mortality rates. Additional research will explore:

Genetic factors that might make some individuals more responsive to Mediterranean diet benefits
The diet's impact on specific cardiovascular conditions
Optimal implementations for different populations and cultures
Cost-effectiveness compared to pharmacological interventions

Conclusion

This comprehensive study provides the strongest evidence yet that diet profoundly impacts cardiovascular health. The Mediterranean diet's 40% reduction in heart disease risk represents a major opportunity for public health improvement.

"If we could get even a quarter of the population to adopt these eating patterns," Dr. Rodriguez reflects, "we could prevent millions of heart attacks and strokes globally. The question now is how we translate research findings into widespread dietary change."

For individuals, the message is clear: transitioning toward Mediterranean eating patterns offers substantial health benefits with minimal risks. Combined with regular physical activity and other healthy lifestyle factors, this dietary approach could be one of the most powerful tools we have for promoting longevity and quality of life.
        """,
        "url": "https://example.com/mediterranean-diet-study",
        "source": "Journal of Medical Research",
        "category": "Health",
        "image_url": "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800",
        "thumb_url": "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=400"
    },
    {
        "title": "Global Tech Giants Rush to Open Development Centers in Tel Aviv",
        "summary": "Tel Aviv emerges as the world's hottest tech hub as dozens of international companies establish R&D facilities in Israel's innovation capital.",
        "content": """
Tel Aviv has become the epicenter of a global tech gold rush, with major corporations from around the world racing to establish research and development centers in Israel's coastal metropolis. This unprecedented wave of investment signals a fundamental shift in the global technology landscape.

The Tel Aviv Advantage

What makes Tel Aviv so attractive to international tech giants? Industry analysts point to several converging factors:

Elite Talent Pool: Israel's unique military service system produces thousands of highly skilled engineers annually. Units like 8200 (cyber intelligence) and Talpiot (elite science program) create talent that rivals or exceeds that found in traditional tech hubs.

Innovation Culture: Israeli startups raised over $25 billion in venture capital last year, the highest per capita globally. This entrepreneurial ecosystem creates constant innovation that established companies want to tap into.

Technical Excellence: Israeli engineers average proficiency in 3-4 programming languages, compared to 2-3 globally. The emphasis on problem-solving and creative thinking produces engineers who excel at tackling complex challenges.

Government Support: The Israeli Innovation Authority offers grants covering up to 50% of R&D costs for international companies establishing facilities in Israel.

The Major Players

The list of companies opening or expanding Tel Aviv operations reads like a who's who of global tech:

Google: Expanding its Tel Aviv campus to 2,000 employees, making it the company's largest development center outside the United States. The facility focuses on core search algorithms, AI research, and cloud infrastructure.

Microsoft: Adding 500 employees to its existing Israeli operations, with new focus areas including quantum computing and advanced cybersecurity. Microsoft has acquired more Israeli companies than from any other country.

Apple: Opening its first Israeli development center with 1,000 employees, focusing on chip design and wireless technologies. Apple has acquired several Israeli chip design companies in recent years.

Amazon: Tripling its Israeli workforce to 3,000, with emphasis on AWS cloud services, machine learning, and logistics optimization.

Meta (Facebook): Expanding to 1,500 employees across Tel Aviv and Haifa, working on VR/AR technologies, connectivity infrastructure, and AI safety.

Nvidia: Growing its Israeli team to 3,000 employees, making Israel the company's largest development center globally. Focus areas include AI chip design and autonomous vehicle technologies.

Intel: Already employing 11,000 in Israel, Intel recently announced a $25 billion investment in a new chip fabrication plant, the largest-ever foreign investment in Israeli history.

The Ecosystem Effect

This concentration of tech giants creates powerful network effects:

Startup Acquisition: Major companies serve as acquirers for successful Israeli startups, creating a virtuous cycle of entrepreneurship and exits.

Talent Circulation: Engineers move between startups and established companies, spreading knowledge and fostering innovation across the ecosystem.

Investment Attraction: The presence of tech giants validates the market, attracting more venture capital and spurring new startup formation.

Academic Collaboration: Companies partner with Israeli universities (Technion, Hebrew University, Tel Aviv University) on cutting-edge research.

Economic Impact

The tech boom is transforming Israel's economy:

Job Creation: The new centers will create approximately 50,000 direct jobs by 2027, with an estimated 100,000 additional indirect jobs in supporting industries.

Salary Growth: Average tech salaries in Tel Aviv have increased 40% over three years, now approaching San Francisco Bay Area levels (though cost of living remains lower).

Real Estate Boom: Commercial real estate prices in Tel Aviv have surged 60% in two years, driven by tech company demand for office space.

Tax Revenue: Tech sector taxes now account for 25% of Israel's corporate tax revenue, funding infrastructure and social programs.

Challenges and Concerns

The rapid growth isn't without complications:

Housing Crisis: Residential real estate prices have skyrocketed, with average Tel Aviv apartments now costing $1 million. The government is fast-tracking housing construction to address the shortage.

Traffic Congestion: Tel Aviv's infrastructure struggles to handle the influx of tech workers. The city is investing $5 billion in public transit expansion, including new subway lines.

Brain Drain Reversal: While the tech boom attracts Israeli talent back from Silicon Valley, some worry about creating economic inequality between tech workers and others.

Geopolitical Concerns: Some companies face criticism for investing in Israel due to the Israeli-Palestinian conflict. Most have maintained their commitment despite occasional controversy.

Quality of Life Balance: The startup culture's demanding work hours are colliding with efforts to maintain work-life balance, sparking discussions about sustainable growth.

The Startup Nation Story

Israel's tech ecosystem didn't emerge overnight. It's the result of decades of intentional policy:

Military Technology Transfer: Sophisticated technologies developed for defense applications are often commercialized by veterans.

Failure-Friendly Culture: Unlike some cultures where business failure carries stigma, Israelis view it as valuable learning experience.

Mandatory Service: The military draft creates networks of talented individuals who often launch startups together after service.

Immigration Policy: Israel's Law of Return has brought waves of skilled immigrants, including 1 million from the former Soviet Union in the 1990s, many with strong technical backgrounds.

Yozma Program: A pioneering government VC fund in the 1990s jumpstarted Israel's venture capital industry.

Future Outlook

Industry observers predict continued growth:

Emerging Technologies: Israel is positioning itself as a leader in quantum computing, autonomous vehicles, and advanced biotechnology.

Sustainability Focus: Clean tech and climate technology startups are attracting increasing attention and investment.

Regional Expansion: Success in Tel Aviv is spreading to other Israeli cities like Haifa, Be'er Sheva, and Jerusalem.

Remote Work Impact: Post-pandemic remote work policies allow companies to tap Israeli talent without full relocation.

The Innovation Challenge

Dr. Yossi Vardi, a veteran Israeli tech entrepreneur, offers perspective: "What makes Israel special isn't just the technology—it's the mindset. Israelis question everything, challenge authority, and believe any problem can be solved. This chutzpah drives innovation."

However, he warns against complacency: "We can't rest on past success. Competition is intensifying from emerging tech hubs worldwide. We must continue investing in education, infrastructure, and maintaining our innovative edge."

Lessons for Other Regions

Cities worldwide study Tel Aviv's success, seeking to replicate it:

Focus on education in STEM fields from early ages
Foster collaboration between military, academia, and industry
Create failure-tolerant business culture
Attract and retain international talent
Invest in infrastructure to support growth

Global Implications

The Tel Aviv tech boom has broader significance:

Diversification: It demonstrates that innovation hubs can succeed outside traditional centers like Silicon Valley.

Talent Distribution: Companies gain access to diverse perspectives and approaches by distributing R&D globally.

Economic Development: It shows how technology can transform national economies relatively quickly.

Geopolitical Influence: Israel's tech strength enhances its diplomatic relationships and global influence.

Conclusion

Tel Aviv's emergence as a premier global tech hub represents one of the most remarkable economic transformations of the 21st century. From a country of 9 million people with few natural resources, Israel has built an innovation ecosystem rivaling much larger nations.

For international tech giants, the decision to invest in Tel Aviv is strategic: access world-class talent, tap into a unique innovation culture, and position themselves at the forefront of emerging technologies.

As one Google executive put it: "We go where the best talent is. In many cutting-edge fields, that means Tel Aviv."

The city's success offers a blueprint for other regions aspiring to build thriving tech ecosystems. But it also presents challenges: maintaining sustainable growth, ensuring broad economic benefits, and preserving quality of life amid rapid change.

One thing seems certain: Tel Aviv's status as a global tech capital is no temporary trend. The convergence of talent, capital, culture, and opportunity has created momentum that will shape the technology industry for decades to come.
        """,
        "url": "https://example.com/tel-aviv-tech-boom",
        "source": "Global Business Journal",
        "category": "Business",
        "image_url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800",
        "thumb_url": "https://images.unsplash.com/photo-486406146926-c627a92ad1ab?w=400"
    }
]


def add_full_articles(db: Session):
    """הוספת מאמרים עם תוכן מלא"""
    added_count = 0
    
    for article_data in FULL_ARTICLES:
        # בדוק אם המאמר כבר קיים
        existing = db.query(Article).filter(Article.url == article_data["url"]).first()
        if existing:
            print(f"⚠️  Article already exists: {article_data['title'][:50]}...")
            continue
        
        # תאריך פרסום אקראי (0-30 ימים אחורה)
        days_ago = random.randint(0, 30)
        published_at = datetime.utcnow() - timedelta(days=days_ago)
        
        # צור מאמר חדש
        article = Article(
            title=article_data["title"],
            summary=article_data["summary"],
            content=article_data["content"],
            url=article_data["url"],
            source=article_data["source"],
            category=article_data["category"],
            image_url=article_data["image_url"],
            thumb_url=article_data["thumb_url"],
            published_at=published_at
        )
        
        db.add(article)
        added_count += 1
        
        print(f"✅ Added: {article_data['title'][:60]}...")
        print(f"   Content: {len(article_data['content'])} characters")
    
    db.commit()
    return added_count


def main():
    """פונקציה ראשית"""
    print("=" * 80)
    print("🚀 Adding Full Content Articles (English)")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        count = add_full_articles(db)
        
        print("\n" + "=" * 80)
        print(f"✅ Success! Added {count} articles with full content")
        print("=" * 80)
        
        # סטטיסטיקה
        total = db.query(Article).count()
        print(f"\n📊 Total articles in system: {total}")
        
        # הצג את המאמרים החדשים
        latest = db.query(Article).order_by(Article.id.desc()).limit(5).all()
        print(f"\n📰 Latest articles:")
        for a in latest:
            content_len = len(a.content) if a.content else 0
            print(f"   ID {a.id}: {a.title[:50]}... ({content_len} chars)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()