import numpy as np
import matplotlib.pyplot as plt

from PIL import Image
from wordcloud import WordCloud, STOPWORDS


# Read the entirety of solely text.
input_file = "..."
text = open(input_file).read()

# read the mask image taken from
# http://www.stencilry.org/stencils/movies/alice%20in%20wonderland/255fk.jpg
image_mask_file = "..."
image_mask = np.array(Image.open(image_mask_file))

stopwords = set(STOPWORDS)
stopwords.add("said")

wc = WordCloud(background_color="white", max_words=2000, mask=image_mask,
               stopwords=stopwords)

# generate word cloud
wc.generate(text)

# manually compute output file from input file and store result there
output_file = "{}-output.png".format(input_file.split(".")[0])
wc.to_file(output_file)

# show
plt.imshow(wc, interpolation='bilinear')
plt.axis("off")
plt.figure()
plt.imshow(image_mask, cmap=plt.cm.gray, interpolation='bilinear')
plt.axis("off")
plt.show()