<script setup>

import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import axios from 'axios'

const imageUrl = ref('')
const uploadRef = ref()
const uploadFile = ref()
const input = ref('')
const resultImageUrl = ref('')
const resultMsg = ref('')

const handleAvatarSuccess = (
  response,
  uploadFile
) => {
  imageUrl.value = URL.createObjectURL(uploadFile.raw)
}

const handleImgChange = (file) => {
  imageUrl.value = URL.createObjectURL(file.raw)
  uploadFile.value = file
}

const beforeAvatarUpload = (rawFile) => {
  if (rawFile.type !== 'image/jpeg') {
    ElMessage.error('Avatar picture must be JPG format!')
    return false
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('Avatar picture size can not exceed 2MB!')
    return false
  }
  return true
}

const handleSubmit = async () => {
  console.log(uploadFile.value.raw)
  console.log(input.value)
  const res = await axios.post('http://127.0.0.1:5000/encode', {
    file: uploadFile.value.raw,
    text: input.value
  }, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })

  let data = res.data
  let splitData = data.split('####')
  resultMsg.value = splitData[0]
  console.info(resultMsg.value)
  let base64Image = splitData[1].split(';base64,').pop()
  let blob = await (await fetch(`data:image/jpeg;base64,${base64Image}`)).blob()
  resultImageUrl.value = URL.createObjectURL(blob)
  console.log(resultImageUrl.value)
}

// //处理解码请求
// const handleDecodeSubmit = async () => {
//   console.log(uploadFile.value.raw)
//   console.log(input.value)
//   const res = await axios.post('http://127.0.0.1:5000/decode', {
//     file: uploadFile.value.raw,
//   }, {
//     headers: {
//       'Content-Type': 'multipart/form-data'
//     }
//   })
// //处理响应
//   let data = res.data
//   let splitData = data.split('####')
//   resultMsg.value = splitData[0]
//   console.info(resultMsg.value)
//   let code = resultMsg.value
//   // let base64Image = splitData[1].split(';base64,').pop()
//   // let blob = await (await fetch(`data:image/jpeg;base64,${base64Image}`)).blob()
//   // resultImageUrl.value = URL.createObjectURL(blob)
//   // console.log(resultImageUrl.value)
// }

</script>

<template>
  <main>
    <div style="display: flex;justify-content: center">
      <div style="display:flex;justify-content: flex-end;align-items: center;flex-direction: column;margin: 16px">
        <el-row>
          <el-upload
            class="avatar-uploader"
            ref="uploadRef"
            action="https://run.mocky.io/v3/9d059bf9-4660-45f2-925d-ce80ad6c4d15"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload"
            :auto-upload="false"
            :on-change="handleImgChange"
          >
            <img v-if="imageUrl" :src="imageUrl" class="avatar" alt="" />
            <el-icon v-else class="avatar-uploader-icon">
              <Plus />
            </el-icon>
          </el-upload>
        </el-row>
        <el-row>
          <el-input v-model="input" placeholder="输入密文" style="width: 160px;margin-top: 16px" />
        </el-row>
        <el-row>
          <el-button style="margin-top: 16px" @click="handleSubmit">提交</el-button>
        </el-row>
      </div>

      <div style="display: flex;justify-content: flex-start;margin: 16px; flex-direction: column">
        <div class="receiveImg">
          <img v-if="resultImageUrl" class="receiveImg" :src="resultImageUrl" alt="" />
        </div>
        <div style="margin-top: 12px">
          <el-text v-text="resultMsg" style="justify-content: center;font-size: 18px" class="mx-1" type="success" szie="large" :src="resultMsg"></el-text>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.avatar-uploader .avatar {
  width: 178px;
  height: 178px;
  display: block;
}
</style>

<style>
.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.el-icon.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
}

.receiveImg {
  width: 178px;
  height: 178px;
  display: block;
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
}

</style>