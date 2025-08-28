import { getPayload } from 'payload'
import config from '../payload.config'
import fs from 'fs'
import path from 'path'

const crawledContent = JSON.parse(
  fs.readFileSync(path.join(__dirname, 'crawled-content.json'), 'utf8')
)

const simpleMigration = async (): Promise<void> => {
  // Temporarily disable cloud storage for migration
  const simpleConfig = {
    ...config,
    plugins: [] // Remove cloud storage plugin for now
  }
  
  const payload = await getPayload({ config: simpleConfig })

  try {
    console.log('🚀 Starting simple content migration...')

    // Create About content
    console.log('📝 Creating About content...')
    const aboutData = {
      title: crawledContent.about.title,
      jobTitle: crawledContent.about.jobTitle,
      profileImage: null,
      biography: {
        root: {
          type: 'root',
          children: [
            {
              type: 'paragraph',
              children: [
                {
                  type: 'text',
                  text: 'Sean grew up as an only child in a single-parent household, raised by his mother with the support of his grandmother and aunt. They were part of the lower-middle class and faced financial challenges. Despite their struggles, Sean\'s mother was determined to provide him with the best education possible.',
                },
              ],
            },
            {
              type: 'paragraph',
              children: [
                {
                  type: 'text',
                  text: 'At 13, Sean began working at McDonald\'s, cleaning floors. One of the most valuable lessons he learned there was the principle of "clean as you go," a philosophy he still applies today.',
                },
              ],
            },
          ],
        },
      },
    }

    await payload.create({
      collection: 'about',
      data: aboutData,
    })

    // Create company entries
    console.log('🏢 Creating company portfolio...')
    for (const company of crawledContent.companies) {
      const companyData = {
        name: company.name,
        description: company.description,
        order: company.order,
        website: company.website || '',
      }

      await payload.create({
        collection: 'companies',
        data: companyData,
      })
      console.log(`✅ Created: ${company.name}`)
    }

    // Create blog posts with clean slugs
    console.log('📰 Creating blog posts...')
    for (const post of crawledContent.blogPosts) {
      // Generate clean slug
      const cleanSlug = post.title
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .trim()

      const postData = {
        title: post.title,
        slug: cleanSlug,
        publishedDate: post.publishedDate,
        excerpt: post.excerpt,
        status: 'published',
        content: {
          root: {
            type: 'root',
            children: [
              {
                type: 'paragraph',
                children: [
                  {
                    type: 'text',
                    text: post.content,
                  },
                ],
              }
            ],
          },
        },
      }

      try {
        await payload.create({
          collection: 'posts',
          data: postData,
        })
        console.log(`📝 Created post: ${post.title}`)
      } catch (error) {
        console.log(`❌ Failed to create post "${post.title}":`, error.message)
      }
    }

    console.log('✅ Simple migration completed!')
    
    // Get final counts
    const companiesCount = await payload.count({ collection: 'companies' })
    const postsCount = await payload.count({ collection: 'posts' })
    const aboutCount = await payload.count({ collection: 'about' })
    
    console.log(`
📊 Migration Results:
- About pages: ${aboutCount.totalDocs}
- Companies: ${companiesCount.totalDocs} / ${crawledContent.companies.length} expected
- Blog posts: ${postsCount.totalDocs} / ${crawledContent.blogPosts.length} expected
    `)

  } catch (error) {
    console.error('❌ Error during migration:', error)
  }

  process.exit(0)
}

simpleMigration()