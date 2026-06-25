export const SPECIES_GROUPS = [
  {
    id: 'snake',
    label: '蛇',
    accent: '#4f8c8b',
    species: ['玉米蛇', '王蛇', '球蟒', '奶蛇', '猪鼻蛇', '蟒蛇']
  },
  {
    id: 'lizard',
    label: '蜥蜴',
    accent: '#b9734f',
    species: ['豹纹守宫', '睫角守宫', '鬃狮蜥', '绿鬣蜥', '蓝舌石龙子', '变色龙']
  },
  {
    id: 'frog',
    label: '蛙',
    accent: '#7a8f62',
    species: ['角蛙', '树蛙', '箭毒蛙', '番茄蛙', '非洲牛蛙']
  },
  {
    id: 'turtle',
    label: '龟',
    accent: '#8a6f4d',
    species: ['巴西龟', '草龟', '地图龟', '剃刀龟', '陆龟', '龟类']
  }
]

export function getSpeciesGroupBySpecies(species) {
  return SPECIES_GROUPS.find((group) => group.species.includes(species)) || SPECIES_GROUPS[0]
}

export function getSpeciesInitial(species) {
  return species?.slice(0, 1) || '宠'
}
