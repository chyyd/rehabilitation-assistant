import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api'
})

export const usePatientStore = defineStore('patient', () => {
  const patients = ref<any[]>([])
  const currentPatient = ref<any | null>(null)
  const loading = ref(false)

  async function fetchPatients() {
    loading.value = true
    try {
      const response = await api.get('/patients')
      patients.value = response.data
    } catch (error) {
      console.error('获取患者列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  async function fetchPatient(hospitalNumber: string) {
    loading.value = true
    try {
      const response = await api.get(`/patients/${hospitalNumber}`)
      currentPatient.value = response.data
      return response.data
    } catch (error) {
      console.error('获取患者信息失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  function selectPatient(patient: any) {
    currentPatient.value = patient
  }

  function clearCurrentPatient() {
    currentPatient.value = null
  }

  return {
    patients,
    currentPatient,
    loading,
    fetchPatients,
    fetchPatient,
    selectPatient,
    clearCurrentPatient
  }
})
