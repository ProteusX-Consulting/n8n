import { getPayload } from 'payload'
import config from '../payload.config'
import fs from 'fs'
import path from 'path'

const crawledContent = JSON.parse(
  fs.readFileSync(path.join(__dirname, 'crawled-content.json'), 'utf8')
)

const completeBlogContent = JSON.parse(
  fs.readFileSync(path.join(__dirname, 'complete-blog-content.json'), 'utf8')
)

const migrateToAtlas = async (): Promise<void> => {
  const payload = await getPayload({ config })

  try {
    console.log('🚀 Starting complete migration to MongoDB Atlas...')

    // 1. Create About content
    console.log('📝 Creating About content...')
    const aboutData = {
      title: crawledContent.about.title,
      jobTitle: crawledContent.about.jobTitle,
      profileImage: null, // Static asset
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
            {
              type: 'paragraph',
              children: [
                {
                  type: 'text',
                  text: crawledContent.about.extendedBio?.education || 'Graduated from Wagner College with degrees in Business, Marketing, and Management. Married to Wileeta McGee with three daughters.',
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

    // 2. Create company portfolio
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

    // 3. Upload blog images
    console.log('📁 Uploading blog images to Atlas...')
    const uploadedMedia: { [key: string]: any } = {}

    const blogImages = [
      {
        filename: 'SRM-1-copia.png',
        alt: 'Larry Reed McGee Portrait',
      },
      {
        filename: 'SRM-2-copia-1024x398.png', 
        alt: 'Larry Reed McGee Memory Photo',
      },
      {
        filename: 'SRM-2-1024x390.png',
        alt: 'Larry Reed McGee with Family',
      }
    ]

    for (const imageInfo of blogImages) {
      const imagePath = path.join(process.cwd(), 'media', imageInfo.filename)
      if (fs.existsSync(imagePath)) {
        try {
          const media = await payload.create({
            collection: 'media',
            data: {
              alt: imageInfo.alt,
            },
            filePath: imagePath,
          })
          uploadedMedia[imageInfo.filename] = media.id
          console.log(`✅ Uploaded: ${imageInfo.filename}`)
        } catch (error) {
          console.log(`⚠️ Could not upload ${imageInfo.filename}:`, error.message)
        }
      }
    }

    // 4. Create blog posts with full content
    console.log('📰 Creating blog posts with full content...')
    
    for (const blogPost of completeBlogContent.blogPosts) {
      try {
        const postData = {
          title: blogPost.title,
          slug: blogPost.slug,
          publishedDate: blogPost.publishedDate,
          excerpt: blogPost.excerpt,
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
                      text: blogPost.content,
                    },
                  ],
                }
              ],
            },
          },
          // Add featured image if available
          ...(blogPost.featuredImage && uploadedMedia[blogPost.featuredImage] && {
            featuredImage: uploadedMedia[blogPost.featuredImage]
          })
        }

        await payload.create({
          collection: 'posts',
          data: postData,
        })
        
        console.log(`✅ Created post: ${blogPost.title}`)
      } catch (error) {
        console.log(`❌ Failed to create "${blogPost.title}":`, error.message)
      }
    }

    // 5. Create admin user
    console.log('👤 Creating admin user...')
    try {
      const adminUser = await payload.create({
        collection: 'users',
        data: {
          name: 'Admin',
          email: 'admin@seanreedmcgee.com',
          password: 'admin123',
        },
      })
      console.log('✅ Admin user created: admin@seanreedmcgee.com / admin123')
    } catch (error) {
      console.log('⚠️ Admin user might already exist')
    }

    // Final summary
    const finalCounts = await Promise.all([
      payload.count({ collection: 'about' }),
      payload.count({ collection: 'companies' }),
      payload.count({ collection: 'posts' }),
      payload.count({ collection: 'media' }),
      payload.count({ collection: 'users' })
    ])

    console.log('✅ Migration to MongoDB Atlas completed!')
    console.log(`
📊 Final Atlas Database Status:
- About pages: ${finalCounts[0].totalDocs}
- Companies: ${finalCounts[1].totalDocs} 
- Blog posts: ${finalCounts[2].totalDocs} (with full content)
- Media files: ${finalCounts[3].totalDocs} 
- Users: ${finalCounts[4].totalDocs}

🎉 All content migrated to MongoDB Atlas!

🔑 Admin Access:
- URL: http://localhost:3000/admin
- Email: admin@seanreedmcgee.com
- Password: admin123

💡 Next steps:
1. Run: npm run dev
2. Visit: http://localhost:3000/admin
3. Login with credentials above
    `)

  } catch (error) {
    console.error('❌ Error during Atlas migration:', error)
  }

  process.exit(0)
}

migrateToAtlas()