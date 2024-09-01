import bchlib
import glob
import os
from PIL import Image,ImageOps
import numpy as np
import tensorflow as tf
import tensorflow.contrib.image
from tensorflow.python.saved_model import tag_constants
from tensorflow.python.saved_model import signature_constants

BCH_POLYNOMIAL = 137
BCH_BITS = 5

def encode_main(encode_readpath, message):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='./stegastamp_pretrained')
    parser.add_argument('--image', type=str, default=encode_readpath)
    parser.add_argument('--images_dir', type=str, default=None)
    parser.add_argument('--save_dir', type=str, default='encoded_image')
    parser.add_argument('--secret', type=str, default=message)
    args = parser.parse_args()
    # args.model = './stegastamp_pretrained'
    # args.image = encode_readpath
    # args.images_dir = None
    # args.save_dir = 'encoded_image'
    # args.secret = message

    #图片编码状态
    status = 'False'

    if args.image is not None:
        files_list = [args.image]
    elif args.images_dir is not None:
        files_list = glob.glob(args.images_dir + '/*')
    else:
        print('Missing input image')
        status = 'False'

    sess = tf.InteractiveSession(graph=tf.Graph())
    try:
        model = tf.saved_model.loader.load(sess, [tag_constants.SERVING], args.model)
    except Exception as e:
        status = 'False'
        return status, ''
    input_secret_name = model.signature_def[signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY].inputs['secret'].name
    input_image_name = model.signature_def[signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY].inputs['image'].name
    input_secret = tf.get_default_graph().get_tensor_by_name(input_secret_name)
    input_image = tf.get_default_graph().get_tensor_by_name(input_image_name)

    output_stegastamp_name = model.signature_def[signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY].outputs['stegastamp'].name
    output_residual_name = model.signature_def[signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY].outputs['residual'].name
    output_stegastamp = tf.get_default_graph().get_tensor_by_name(output_stegastamp_name)
    output_residual = tf.get_default_graph().get_tensor_by_name(output_residual_name)

    width = 400
    height = 400

    bch = bchlib.BCH(BCH_POLYNOMIAL, BCH_BITS)

    if len(args.secret) > 7:
        print('Error: Can only encode 56bits (7 characters) with ECC')
        status = 'False'

    data = bytearray(args.secret + ' '*(7-len(args.secret)), 'utf-8')
    ecc = bch.encode(data)
    packet = data + ecc

    packet_binary = ''.join(format(x, '08b') for x in packet)
    secret = [int(x) for x in packet_binary]
    secret.extend([0,0,0,0])

    file_path = None
    if args.save_dir is None:
        print('save_dir not exist!')
        status = 'False'
    if args.save_dir is not None:
        if not os.path.exists(args.save_dir):
            os.makedirs(args.save_dir)
        size = (width, height)
        for filename in files_list:
            image = Image.open(filename).convert("RGB")
            image = np.array(ImageOps.fit(image,size),dtype=np.float32)
            image /= 255.

            # image = image.reshape(100,100,3)
            feed_dict = {input_secret:[secret],
                         input_image:[image]}

            hidden_img, residual = sess.run([output_stegastamp, output_residual],feed_dict=feed_dict)

            rescaled = (hidden_img[0] * 255).astype(np.uint8)
            raw_img = (image * 255).astype(np.uint8)
            residual = residual[0]+.5

            residual = (residual * 255).astype(np.uint8)

            save_name = filename.split('/')[-1].split('.')[0]

            im = Image.fromarray(np.array(rescaled))
            # im.save(args.save_dir + '/'+save_name+'_hidden.png')
            im.save(save_name+'_hidden.png')
            # file_path = args.save_dir + '/'+save_name+'_hidden.png'
            file_path = save_name+'_hidden.png'

            im = Image.fromarray(np.squeeze(np.array(residual)))
            # im.save(args.save_dir + '/'+save_name+'_residual.png')
            im.save(save_name+'_residual.png')
            # file_path = save_name+'_residual.png'

            status = 'True'
    return status,file_path

if __name__ == "__main__":
    encode()
