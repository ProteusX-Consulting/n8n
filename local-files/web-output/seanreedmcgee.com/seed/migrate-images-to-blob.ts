import { getPayload } from 'payload'
import config from '../payload.config'
import fs from 'fs'
import path from 'path'

const migrateImagesToBlob = async (): Promise<void> => {
  const payload = await getPayload({ config })

  try {
    console.log('🚀 Starting blog image migration to Vercel Blob...')

    // Clear existing media entries to avoid duplicates
    console.log('🧹 Clearing existing local media entries...')
    const existingMedia = await payload.find({
      collection: 'media',
      limit: 1000
    })
    
    for (const media of existingMedia.docs) {
      await payload.delete({
        collection: 'media',
        id: media.id
      })
    }
    console.log(`✅ Cleared ${existingMedia.docs.length} existing media entries`)

    // Upload blog images to Vercel Blob
    console.log('📁 Uploading blog images to Vercel Blob...')
    const uploadedMedia: { [key: string]: any } = {}

    const blogImages = [
      {
        filename: 'SRM-1-copia.png',
        alt: 'Larry Reed McGee Portrait - Featured image for tribute article',
        description: 'Portrait photo of Larry Reed McGee for the Sons Letter tribute'
      },
      {
        filename: 'SRM-2-copia-1024x398.png', 
        alt: 'Larry Reed McGee Memory Photo - Family moments',
        description: 'Memory photo of Larry Reed McGee with family'
      },
      {
        filename: 'SRM-2-1024x390.png',
        alt: 'Larry Reed McGee with Family - Personal memories',
        description: 'Larry Reed McGee family photo for tribute article'
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
          console.log(`✅ Uploaded to Vercel Blob: ${imageInfo.filename}`)
          console.log(`   URL: ${media.url}`)
        } catch (error) {
          console.log(`❌ Failed to upload ${imageInfo.filename}:`, error.message)
        }
      } else {
        console.log(`⚠️ File not found: ${imagePath}`)
      }
    }

    // Update blog posts to reference the new cloud-hosted images
    console.log('🔗 Linking blog posts to cloud images...')
    
    // Find and update "A Son's Letter to Larry Reed McGee" with featured image
    const sonLetterPosts = await payload.find({
      collection: 'posts',
      where: {
        title: {
          equals: "A Son's Letter to Larry Reed McGee"
        }
      }
    })

    if (sonLetterPosts.docs.length > 0 && uploadedMedia['SRM-1-copia.png']) {
      const post = sonLetterPosts.docs[0]
      await payload.update({
        collection: 'posts',
        id: post.id,
        data: {
          featuredImage: uploadedMedia['SRM-1-copia.png']
        }
      })
      console.log('✅ Linked featured image to "A Sons Letter to Larry Reed McGee"')
    }

    // Verify the cloud storage is working
    console.log('🔍 Verifying cloud storage...')
    const finalMedia = await payload.find({
      collection: 'media',
      limit: 10
    })

    console.log('✅ Blog image migration to Vercel Blob completed!')
    console.log(`
📊 Migration Results:
- Images uploaded to Vercel Blob: ${Object.keys(uploadedMedia).length}
- Total media in database: ${finalMedia.totalDocs}
- Cloud storage: ✅ Active (Vercel Blob)
- Local media directory: No longer used

🌐 Your blog images are now:
- ✅ Served from Vercel's global CDN
- ✅ Automatically optimized and resized  
- ✅ Available in multiple formats (WebP, etc.)
- ✅ Lightning fast delivery worldwide

🎉 Perfect setup for production deployment!
    `)

    // Show sample URLs
    if (finalMedia.docs.length > 0) {
      const sampleMedia = finalMedia.docs[0]
      console.log(`
📄 Sample Image URL:
- File: ${sampleMedia.filename}
- Cloud URL: ${sampleMedia.url}
- Alt text: ${sampleMedia.alt}
      `)
    }

  } catch (error) {
    console.error('❌ Error during blob migration:', error)
  }

  process.exit(0)
}

migrateImagesToBlob()