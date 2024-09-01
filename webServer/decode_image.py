import bchlib
import glob
from PIL import Image, ImageOps
import numpy as np
import tensorflow as tf
import tensorflow.contrib.image
from tensorflow.python.saved_model import tag_constants
from tensorflow.python.saved_model import signature_constants

BCH_POLYNOMIAL = 137
BCH_BITS = 5

def decode_main(decode_path):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str,default='./stegastamp_pretrained')
    parser.add_argument('--image', type=str, default=decode_path)
    parser.add_argument('--images_dir', type=str, default=None)
    parser.add_argument('--secret_size', type=int, default=100)
    args = parser.parse_args()
    # args.model = './stegastamp_pretrained'
    # args.image = decode_path
    # args.images_dir = None
    # args.secret_size = 100
    status = 'False'

    if args.image is not None:
        files_list = [args.image]
    elif args.images_dir is not None:
        files_list = glob.glob(args.images_dir + '/*')
    else:
        print('Missing input image')
        return

    sess = tf.InteractiveSession(graph=tf.Graph())
    try:
        model = tf.saved_model.loader.load(sess, [tag_constants.SERVING], args.model)
    except Exception as e:
        status = 'False'
        return status,''
    input_image_name = model.signature_def[signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY].inputs['image'].name
    input_image = tf.get_default_graph().get_tensor_by_name(input_image_name)

    output_secret_name = model.signature_def[signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY].outputs['decoded'].name
    output_secret = tf.get_default_graph().get_tensor_by_name(output_secret_name)

    # status = True
    bch = bchlib.BCH(BCH_POLYNOMIAL, BCH_BITS)
    fileName = ''
    code = ''
    for filename in files_list:
        image = Image.open(filename).convert("RGB")
        image = np.array(ImageOps.fit(image,(400, 400)),dtype=np.float32)
        image /= 255.

        feed_dict = {input_image:[image]}

        secret = sess.run([output_secret],feed_dict=feed_dict)[0][0]

        packet_binary = "".join([str(int(bit)) for bit in secret[:96]])
        packet = bytes(int(packet_binary[i : i + 8], 2) for i in range(0, len(packet_binary), 8))
        packet = bytearray(packet)

        data, ecc = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]

        bitflips = bch.decode_inplace(data, ecc)

        if bitflips != -1:
            try:
                code = data.decode("utf-8")
                fileName = filename
                # print(filename, code)
                status = True
                continue
            except:
                continue
        status = 'False'
        fileName = filename
        # print(filename, 'Failed to decode')

    if status == 'False':
        print(fileName, 'Failed to decode')
    if status == 'True':
        print('Decode success',fileName,code)
    return (status, code)


if __name__ == "__main__":
    decode()
