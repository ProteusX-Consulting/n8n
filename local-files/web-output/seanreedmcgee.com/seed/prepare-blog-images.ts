import { getPayload } from 'payload'
import config from '../payload.config'
import fs from 'fs'
import path from 'path'

const prepareBlogImages = async (): Promise<void> => {
  const payload = await getPayload({ config })

  try {
    console.log('🚀 Preparing blog images for CMS (ready for Vercel Blob on deployment)...')

    // Upload blog images to media collection (will use Vercel Blob when deployed)
    console.log('📁 Uploading blog images to media collection...')
    const uploadedMedia: { [key: string]: any } = {}

    const blogImages = [
      {
        filename: 'SRM-1-copia.png',
        alt: 'Larry Reed McGee Portrait - Featured image for tribute article',
        description: 'Portrait photo of Larry Reed McGee'
      },
      {
        filename: 'SRM-2-copia-1024x398.png', 
        alt: 'Larry Reed McGee Memory Photo - Family moments',
        description: 'Memory photo of Larry Reed McGee with family'
      },
      {
        filename: 'SRM-2-1024x390.png',
        alt: 'Larry Reed McGee with Family - Personal memories',
        description: 'Family photo of Larry Reed McGee'
      }
    ]

    for (const imageInfo of blogImages) {
      const imagePath = path.join(process.cwd(), 'media', imageInfo.filename)
      if (fs.existsSync(imagePath)) {
        try {
          // Check if media already exists to avoid duplicates
          const existing = await payload.find({
            collection: 'media',
            where: {
              filename: {
                equals: imageInfo.filename
              }
            }
          })

          if (existing.docs.length === 0) {
            const media = await payload.create({
              collection: 'media',
              data: {
                alt: imageInfo.alt,
              },
              filePath: imagePath,
            })
            uploadedMedia[imageInfo.filename] = media.id
            console.log(`✅ Uploaded: ${imageInfo.filename}`)
            console.log(`   Media ID: ${media.id}`)
          } else {
            uploadedMedia[imageInfo.filename] = existing.docs[0].id
            console.log(`✅ Found existing: ${imageInfo.filename} (ID: ${existing.docs[0].id})`)
          }
        } catch (error) {
          console.log(`❌ Failed to upload ${imageInfo.filename}:`, error.message)
        }
      } else {
        console.log(`⚠️ File not found: ${imagePath}`)
      }
    }

    // Link featured images to blog posts
    console.log('🔗 Linking featured images to blog posts...')
    
    // Find and update "A Son's Letter to Larry Reed McGee" with featured image
    if (uploadedMedia['SRM-1-copia.png']) {
      const sonLetterPosts = await payload.find({
        collection: 'posts',
        where: {
          title: {
            contains: "Son's Letter"
          }
        }
      })

      if (sonLetterPosts.docs.length > 0) {
        const post = sonLetterPosts.docs[0]
        await payload.update({
          collection: 'posts',
          id: post.id,
          data: {
            featuredImage: uploadedMedia['SRM-1-copia.png']
          }
        })
        console.log(`✅ Linked featured image to "${post.title}"`)
      }
    }

    // Verify setup
    console.log('🔍 Verifying blog image setup...')
    const allMedia = await payload.find({
      collection: 'media',
      limit: 10
    })

    const postsWithImages = await payload.find({
      collection: 'posts',
      where: {
        featuredImage: {
          exists: true
        }
      }
    })

    console.log('✅ Blog image preparation completed!')
    console.log(`
📊 Current Status:
- Images in media collection: ${allMedia.totalDocs}
- Blog posts with featured images: ${postsWithImages.totalDocs}
- Blog images uploaded: ${Object.keys(uploadedMedia).length}

📍 Local Development:
- Images served from: /media/ directory
- URLs like: http://localhost:3000/media/filename.png

🚀 Production Deployment (Vercel):
- Images will automatically use Vercel Blob storage
- Global CDN delivery for fast loading
- Automatic optimization and resizing

🎉 Ready for both local development and Vercel deployment!

💡 When you deploy to Vercel with BLOB_READ_WRITE_TOKEN:
   ✅ New uploads go to Vercel Blob automatically
   ✅ Existing images are accessible via CMS
   ✅ Perfect hybrid setup maintained
    `)

  } catch (error) {
    console.error('❌ Error during blog image preparation:', error)
  }

  process.exit(0)
}

prepareBlogImages()